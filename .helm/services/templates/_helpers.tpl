{{/*
Expand the name of the chart.
*/}}
{{- define "deps-file-storage.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "deps-file-storage.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "deps-file-storage.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "deps-file-storage.labels" -}}
helm.sh/chart: {{ include "deps-file-storage.chart" . }}
{{ include "deps-file-storage.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "deps-file-storage.selectorLabels" -}}
app.kubernetes.io/name: {{ include "deps-file-storage.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "deps-file-storage.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "deps-file-storage.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Vault secrets annotations
*/}}
{{- define "deps-file-storage.vaultAnnotations" -}}
vault.security.banzaicloud.io/vault-addr: "{{ .Values.inject_secrets.vault_address }}"
vault.security.banzaicloud.io/vault-auth-method: kubernetes
vault.security.banzaicloud.io/vault-path: {{ .Values.inject_secrets.vault_path }}
vault.security.banzaicloud.io/vault-namespace: {{ .Values.inject_secrets.vault_namespace }}
vault.security.banzaicloud.io/vault-role: {{ .Values.inject_secrets.vault_role }}
vault.security.banzaicloud.io/vault-serviceaccount: {{ .Values.inject_secrets.vault_serviceaccount }}
vault.security.banzaicloud.io/vault-skip-verify: "true"
{{- end }}
