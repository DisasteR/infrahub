---
label: Repository config file
icon: tools
layout: default
---
# Repository configuration file

The repository configuration file allows you to define multiple resources that need to be imported into Infrahub.

The file should be formatted as a Yaml file, have the filename `.infrahub.yml` and should be stored at the root of the [repository](/topics/repository).

!!!info
See [this topic](/topics/infrahub-yml) for more details on the available repository configuration options
!!!

## Check Definitions

**Description**: User defined checks  
**Key**: check_definitions  
**Type**: array  
**Item type**: InfrahubCheckDefinitionConfig  

| Property | Type | Description | Mandatory | { class="compact" }
| -------- | ---- | ----------- | --------- |
| name | string | The name of the Check Definition | True |
| file_path | string | The file within the repository with the check code. | True |
| parameters | object | The input parameters required to run this check | False |
| targets | string | The group to target when running this check, leave blank for global checks | False |
| class_name | string | The name of the check class to run. | False |

## Schemas

**Description**: Schema files  
**Key**: schemas  
**Type**: array  
**Item type**: string  
**Item format**: path

## Jinja2 Transforms

**Description**: Jinja2 data transformations  
**Key**: jinja2_transforms  
**Type**: array  
**Item type**: InfrahubJinja2TransformConfig  

| Property | Type | Description | Mandatory | { class="compact" }
| -------- | ---- | ----------- | --------- |
| name | string | The name of the transform | True |
| query | string | The name of the GraphQL Query | True |
| template_path | string | The path within the repository of the template file | True |
| description | string | Description for this transform | False |

## Artifact Definitions

**Description**: Artifact definitions  
**Key**: artifact_definitions  
**Type**: array  
**Item type**: InfrahubRepositoryArtifactDefinitionConfig  

| Property | Type | Description | Mandatory | { class="compact" }
| -------- | ---- | ----------- | --------- |
| name | string | The name of the artifact definition | True |
| artifact_name | string | Name of the artifact created from this definition | False |
| parameters | object | The input parameters required to render this artifact | True |
| content_type | string | The content type of the rendered artifact | True |
| targets | string | The group to target when creating artifacts | True |
| transformation | string | The transformation to use. | True |

## Python Transforms

**Description**: Python data transformations  
**Key**: python_transforms  
**Type**: array  
**Item type**: InfrahubPythonTransformConfig  

| Property | Type | Description | Mandatory | { class="compact" }
| -------- | ---- | ----------- | --------- |
| name | string | The name of the Transform | True |
| file_path | string | The file within the repository with the transform code. | True |
| class_name | string | The name of the transform class to run. | False |