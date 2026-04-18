from typing import Any, Dict, Optional, Type, Union

from dependency_injector import containers, providers, resources
from deps_asb import ASBClient, ASBConsumer, ASBProducer
from deps_async_datasource import AsyncDatabase
from deps_kafka import KafkaClient, KafkaConsumer, KafkaProducer
from deps_message_flow import MessagingDriverEnum
from deps_message_flow.messaging.consumer import IMessageConsumer
from deps_message_flow.messaging.producer import IMessageProducer
from deps_rabbitmq import RabbitMQClient, RabbitMQConsumer, RabbitMQProducer

from deps_file_storage.constants import PROJECT_NAME
from deps_file_storage.domain.async_services import AsyncStorageService
from deps_file_storage.domain.services import StorageService
from deps_file_storage.events_handler import make_consumer
from deps_file_storage.extras.auth import (
    APIKeyAuthService,
    DepsAuthService,
    JWTAuthService,
)
from deps_file_storage.extras.datasource import Database
from deps_file_storage.infrastructure.access_management import (
    AsyncDummyAccessManager,
    AsyncOrganisationBasedAccessManager,
    AsyncStorageServiceAccessor,
    AsyncUserBasedAccessManager,
)
from deps_file_storage.infrastructure.access_management.storage_access_manager import (
    DummyAccessManager,
    OrganisationBasedAccessManager,
    UserBasedAccessManager,
)
from deps_file_storage.infrastructure.access_management.storage_services_accessor import (
    StorageServiceAccessor,
)
from deps_file_storage.infrastructure.async_repositories import (
    AsyncOrganisationHasFileRepository,
    AsyncUserHasFileRepository,
)
from deps_file_storage.infrastructure.repositories import (
    OrganisationHasFileRepository,
    UserHasFileRepository,
)
from deps_file_storage.storage import (
    AsyncAzureStorageService,
    AsyncFileStorage,
    AsyncGCPStorageService,
    AzureStorageService,
    FileStorageService,
    GCPStorageService,
    S3StorageService,
)

MessagingClient = Union[ASBClient, KafkaClient, RabbitMQClient]


class AsyncDatabaseResource(resources.AsyncResource):
    async def init(
        self,
        username: str,
        password: str,
        host: str,
        port: int,
        database: str,
        require_secure_transport: bool,
        sslkey: str,
        sslcert: str,
        sslrootcert: str,
        sslmode: str,
    ):
        db = AsyncDatabase(
            username=username,
            password=password,
            host=host,
            port=port,
            database=database,
            require_secure_transport=require_secure_transport,
            sslkey=sslkey,
            sslcert=sslcert,
            sslrootcert=sslrootcert,
            sslmode=sslmode,
        )
        await db.connect()
        return db

    async def shutdown(self, resource: AsyncDatabase) -> None:
        await resource.close()


class MessageBrokerResource(resources.Resource):
    def init(
        self,
        driver_type: str,
        expected_driver: str,
        client: Type[MessagingClient],
        message_connection_string: str,
        **kwargs: Dict[str, Any],
    ) -> Optional[MessagingClient]:
        return client(message_connection_string, **kwargs) if driver_type == expected_driver else None

    def shutdown(self, resource: Optional[MessagingClient]) -> None:
        if resource:
            resource.close()


class Datasources(containers.DeclarativeContainer):
    config = providers.Configuration()

    database: providers.Provider[Database] = providers.Singleton(
        Database,
        username=config.user,
        password=config.password,
        host=config.host,
        port=config.port,
        database=config.db,
        dialect=config.dialect,
        driver=config.driver,
        require_secure_transport=config.require_secure_transport,
        sslkey=config.ssl.key,
        sslcert=config.ssl.cert,
        sslrootcert=config.ssl.rootcert,
        sslmode=config.ssl.mode,
        pool_size=config.pool_size,
    )
    async_database: providers.Provider[AsyncDatabase] = providers.Resource(
        AsyncDatabaseResource,
        username=config.user,
        password=config.password,
        host=config.host,
        port=config.port,
        database=config.db,
        require_secure_transport=config.require_secure_transport,
        sslkey=config.ssl.key,
        sslcert=config.ssl.cert,
        sslrootcert=config.ssl.rootcert,
        sslmode=config.ssl.mode,
    )


class MessageBrokers(containers.DeclarativeContainer):
    config = providers.Configuration()
    messaging_driver_settings = providers.Dependency(instance_of=object)

    broker_client: providers.Provider[MessagingClient] = providers.Selector(
        config.messaging_driver,
        asb=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.ASB.value,
            expected_driver=config.messaging_driver,
            client=ASBClient,
            message_connection_string=config.message_broker_connection_string,
            asb_settings=messaging_driver_settings,
        ),
        kafka=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.KAFKA.value,
            expected_driver=config.messaging_driver,
            client=KafkaClient,
            message_connection_string=config.message_broker_connection_string,
            settings=messaging_driver_settings,
        ),
        rabbitmq=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.RABBITMQ.value,
            expected_driver=config.messaging_driver,
            client=RabbitMQClient,
            message_connection_string=config.message_broker_connection_string,
            settings=messaging_driver_settings,
        ),
    )


class Messaging(containers.DeclarativeContainer):
    config = providers.Configuration()
    message_brokers = providers.DependenciesContainer()

    producer: providers.Provider[IMessageProducer] = providers.Selector(
        config.messaging_driver,
        asb=providers.Singleton(
            ASBProducer,
            client=message_brokers.broker_client,
            topic_name=config.messaging_driver_settings.topic_name,
        ),
        kafka=providers.Singleton(
            KafkaProducer,
            client=message_brokers.broker_client,
        ),
        rabbitmq=providers.Singleton(
            RabbitMQProducer,
            client=message_brokers.broker_client,
        ),
    )
    consumer: providers.Provider[IMessageConsumer] = providers.Selector(
        config.messaging_driver,
        asb=providers.Singleton(
            ASBConsumer,
            client=message_brokers.broker_client,
            topic_name=config.messaging_driver_settings.topic_name,
            custom_subscription_name=PROJECT_NAME,
        ),
        kafka=providers.Singleton(
            KafkaConsumer,
            client=message_brokers.broker_client,
        ),
        rabbitmq=providers.Singleton(
            RabbitMQConsumer,
            client=message_brokers.broker_client,
        ),
    )


class Repositories(containers.DeclarativeContainer):
    datasources = providers.DependenciesContainer()
    user_has_file_repository: providers.Provider[UserHasFileRepository] = providers.Singleton(
        UserHasFileRepository,
        datasources.database,
    )
    organisation_has_file_repository: providers.Provider[OrganisationHasFileRepository] = providers.Singleton(
        OrganisationHasFileRepository,
        datasources.database,
    )
    async_organisation_has_file_repository: providers.Provider[AsyncOrganisationHasFileRepository] = providers.Singleton(
        AsyncOrganisationHasFileRepository,
        datasources.async_database,
    )
    async_user_has_file_repository: providers.Provider[AsyncUserHasFileRepository] = providers.Singleton(
        AsyncUserHasFileRepository,
        datasources.async_database,
    )


class Containers(containers.DeclarativeContainer):
    config = providers.Configuration()
    repositories = providers.DependenciesContainer()
    messaging = providers.DependenciesContainer()

    storage_service_access_manager: providers.Provider = providers.Selector(
        config.authentication.storage_permission_rule,
        none=providers.Singleton(DummyAccessManager),
        user=providers.Factory(
            UserBasedAccessManager,
            repositories.user_has_file_repository,
            config.authentication.admins_group,
        ),
        organisation=providers.Factory(
            OrganisationBasedAccessManager,
            repositories.organisation_has_file_repository,
        ),
    )

    async_storage_service_access_manager: providers.Provider = providers.Selector(
        config.authentication.storage_permission_rule,
        none=providers.Singleton(AsyncDummyAccessManager),
        user=providers.Singleton(
            AsyncUserBasedAccessManager,
            repositories.async_user_has_file_repository,
            config.authentication.admins_group,
        ),
        organisation=providers.Singleton(
            AsyncOrganisationBasedAccessManager,
            repositories.async_organisation_has_file_repository,
        ),
    )

    storage_service: providers.Provider[StorageService] = providers.Factory(
        StorageService,
        registered_storages=providers.Dict(
            FILE_STORAGE=providers.DelegatedSingleton(
                FileStorageService,
                config.media_root,
                config.acceptable_mimetypes,
                config.cipher_key,
            ),
            GCP_STORAGE=providers.DelegatedSingleton(
                GCPStorageService,
                config.gcp_storage.bucket_name,
                config.gcp_storage.auth_key,
                config.gcp_storage.media_expires,
                config.gcp_storage.use_emulator,
            ),
            S3_STORAGE=providers.DelegatedSingleton(
                S3StorageService,
                config.s3_storage,
                config.acceptable_mimetypes,
            ),
            AZURE_STORAGE=providers.DelegatedSingleton(
                AzureStorageService,
                connection_string=config.azure_storage.connection_string,
                container_name=config.azure_storage.container_name,
            ),
        ),
    )

    async_storage_service: providers.Provider[AsyncStorageService] = providers.Singleton(
        AsyncStorageService,
        registered_storages=providers.Dict(
            FILE_STORAGE=providers.DelegatedSingleton(
                AsyncFileStorage,
                config.media_root,
            ),
            AZURE_STORAGE=providers.DelegatedSingleton(
                AsyncAzureStorageService,
                connection_string=config.azure_storage.connection_string,
                container_name=config.azure_storage.container_name,
            ),
            GCP_STORAGE=providers.DelegatedSingleton(
                AsyncGCPStorageService,
                bucket_name=config.gcp_storage.bucket_name,
                auth_key=config.gcp_storage.auth_key,
                media_expires=config.gcp_storage.media_expires,
            ),
        ),
    )

    storage_service_accessor: providers.Provider[StorageServiceAccessor] = providers.Factory(
        StorageServiceAccessor,
        storage_service,
        storage_service_access_manager,
    )

    async_storage_service_accessor: providers.Provider[AsyncStorageServiceAccessor] = providers.Singleton(
        AsyncStorageServiceAccessor,
        async_storage_service,
        async_storage_service_access_manager,
    )

    jwt_auth_service: providers.Provider[JWTAuthService] = providers.Singleton(
        JWTAuthService,
        config.authentication.certs_endpoint,
        config.authentication.encryption_algorithm,
        config.authentication.verify_ssl,
    )
    api_key_auth_service: providers.Provider[APIKeyAuthService] = providers.Singleton(
        APIKeyAuthService,
        config.authentication.api_key,
    )
    deps_auth_service: providers.Provider[DepsAuthService] = providers.Singleton(
        DepsAuthService,
        jwt_auth_service,
        api_key_auth_service,
    )
    consumer: providers.Singleton[IMessageConsumer] = providers.Singleton(
        make_consumer,
        messaging.consumer,
        messaging.producer,
    )


class Core(containers.DeclarativeContainer):
    config = providers.Configuration()
    build_info: providers.Provider[Dict] = providers.Dict(
        {
            "build_tag": config.service_info.tag,
            "build_date": config.service_info.date,
            "commit_hash": config.service_info.hash,
        },
    )


class Application(containers.DeclarativeContainer):
    config = providers.Configuration()
    messaging_driver_settings = providers.Dependency(instance_of=object)
    datasources: providers.Container[Datasources] = providers.Container(
        Datasources,
        config=config.database,
    )
    message_brokers: providers.Container[MessageBrokers] = providers.Container(
        MessageBrokers,
        config=config,
        messaging_driver_settings=messaging_driver_settings,
    )
    repositories: providers.Container[Repositories] = providers.Container(
        Repositories,
        datasources=datasources,
    )
    messaging: providers.Container[Messaging] = providers.Container(
        Messaging,
        config=config,
        message_brokers=message_brokers,
    )
    containers: providers.Container[Containers] = providers.Container(
        Containers,
        config=config,
        repositories=repositories,
        messaging=messaging,
    )
    core: providers.Container[Core] = providers.Container(Core, config=config)
