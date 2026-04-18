from uuid import uuid4


class TestUserHasFileRepository:
    def test_add_file_to_user__file_added__user_can_get_filename(self, repositories, faker):
        user_pk, filename = uuid4().hex, faker.file_name()
        repositories.user_has_file_repository().add_file_to_user(filename, user_pk)

        user_files = repositories.user_has_file_repository().get_user_files(user_pk)

        assert filename in user_files

    def test_get_user_files__multiple_files__all_files_returned(self, repositories, faker):
        user_pk = uuid4().hex
        files = [faker.file_name() for _ in range(3)]
        for file in files:
            repositories.user_has_file_repository().add_file_to_user(file, user_pk)

        user_files = repositories.user_has_file_repository().get_user_files(user_pk)

        assert all(file in user_files for file in files)

    def test_add_file_for_users__2_users_add_files__both_users_get_their_files(self, repositories, faker):
        user_pk_1, user_pk_2 = uuid4().hex, uuid4().hex
        user_1_files = [faker.file_name() for _ in range(3)]
        user_2_files = [faker.file_name() for _ in range(3)]

        for file in user_1_files:
            repositories.user_has_file_repository().add_file_to_user(file, user_pk_1)

        for file in user_2_files:
            repositories.user_has_file_repository().add_file_to_user(file, user_pk_2)

        files_for_user_1 = repositories.user_has_file_repository().get_user_files(user_pk_1)
        files_for_user_2 = repositories.user_has_file_repository().get_user_files(user_pk_2)

        assert all(f in user_1_files for f in files_for_user_1)
        assert all(f in user_2_files for f in files_for_user_2)

    def test_remove_file_from_user__file_exists__record_removed_from_database(self, repositories, faker):
        user_pk, filename = uuid4().hex, uuid4().hex
        repositories.user_has_file_repository().add_file_to_user(filename, user_pk)

        removed = repositories.user_has_file_repository().remove_file_from_users(filename)
        files = repositories.user_has_file_repository().get_user_files(user_pk)

        assert removed is True
        assert filename not in files

    def test_remove_file_from_user__file_does_not_exist__false_returned(self, repositories, faker):
        removed = repositories.user_has_file_repository().remove_file_from_users("this_file_does_not_exist")

        assert removed is False
