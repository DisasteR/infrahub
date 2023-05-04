QUERY_ALL_REPOSITORIES = """
query {
    repository {
        id
        name {
            value
        }
        location {
            value
        }
        commit {
            value
        }
    }
}
"""


QUERY_ALL_TRANSFORM_PYTHON = """
query {
    transform_python {
        id
        name {
            value
        }
        description {
            value
        }
        file_path {
            value
        }
        class_name {
            value
        }
        rebase {
            value
        }
        timeout {
            value
        }
        url {
            value
        }
        query {
            id
            name {
                value
            }
        }
        repository {
            id
            name {
                value
            }
        }
    }
}
"""

QUERY_ALL_BRANCHES = """
query {
    branch {
        id
        name
        description
        origin_branch
        branched_from
        is_default
        is_data_only
    }
}
"""
QUERY_BRANCH_DIFF = """
            query($branch_name: String!, $branch_only: Boolean!, $diff_from: String!, $diff_to: String! ) {
                diff(branch: $branch_name, branch_only: $branch_only, time_from: $diff_from, time_to: $diff_to ) {
                    nodes {
                        branch
                        kind
                        id
                        changed_at
                        action
                        attributes {
                            name
                            id
                            changed_at
                            action
                            properties {
                                action
                                type
                                changed_at
                                branch
                                value {
                                    previous
                                    new
                                }
                            }
                        }
                    }
                    relationships {
                        branch
                        id
                        name
                        properties {
                            branch
                            type
                            changed_at
                            action
                            value {
                                previous
                                new
                            }
                        }
                        nodes {
                            id
                            kind
                        }
                        changed_at
                        action
                    }
                    files {
                        action
                        repository
                        branch
                        location
                    }
                }
            }
            """

MUTATION_COMMIT_UPDATE = """
mutation ($repository_id: String!, $commit: String!) {
    repository_update(data: { id: $repository_id, commit: { value: $commit } }) {
        ok
        object {
            commit {
                value
            }
        }
    }
}
"""


MUTATION_TRANSFORM_PYTHON_CREATE = """
mutation($name: String!, $description: String!, $file_path: String!, $class_name: String!, $repository: String!, $query: String!, $url: String!, $timeout: Int!, $rebase: Boolean!) {
  transform_python_create(data: {
    name: { value: $name }
    description: { value: $description }
    query: { id: $query }
    file_path: { value: $file_path }
    url: { value: $url }
    class_name: { value: $class_name }
    repository: { id: $repository }
    timeout: { value: $timeout }
    rebase: { value: $rebase }
  }){
        ok
        object {
            id
            name {
                value
            }
        }
    }
}
"""

MUTATION_TRANSFORM_PYTHON_UPDATE = """
mutation($id: String!, $name: String!, $description: String!, $file_path: String!, $class_name: String!, $query: String!, $url: String!, $timeout: Int!, $rebase: Boolean!) {
  transform_python_update(data: {
    id: $id
    name: { value: $name },
    description: { value: $description },
    file_path: { value: $file_path },
    class_name: { value: $class_name },
    url: { value: $url },
    query: { id: $query },
    timeout: { value: $timeout },
    rebase: { value: $rebase },
  }){
        ok
        object {
            id
            name {
                value
            }
        }
    }
}
"""


QUERY_SCHEMA = """
    query {
        node_schema {
            name {
                value
            }
            kind {
                value
            }
            inherit_from {
                value
            }
            description {
                value
            }
            default_filter {
                value
            }
            attributes {
                name {
                    value
                }
                kind {
                    value
                }
                optional {
                    value
                }
                unique {
                    value
                }
                default_value {
                    value
                }
            }
            relationships {
                name {
                    value
                }
                peer {
                    value
                }
                identifier {
                    value
                }
                cardinality {
                    value
                }
                optional {
                    value
                }
            }
        }
    }
    """
