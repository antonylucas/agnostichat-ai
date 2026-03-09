import copy


def get_field_type(mapping, field_path):
    """
    Retorna o tipo do campo a partir do mapping dado um caminho (ex: 'visitor_id').
    """
    props = mapping.get("properties", {})
    parts = field_path.split(".")
    for part in parts:
        if part in props:
            info = props[part]
            if "type" in info:
                return info["type"], info
            elif "properties" in info:
                props = info["properties"]
            else:
                return None, info
        else:
            return None, None
    return None, None


def has_keyword_subfield(field_info):
    """
    Verifica se o campo possui subcampo keyword.
    """
    if not field_info:
        return False
    fields = field_info.get("fields", {})
    return "keyword" in fields


def ajustar_query_keyword(query_dsl, mapping):
    """
    Ajusta a query DSL para usar .keyword em agregações de campos text, se disponível.
    """
    query = copy.deepcopy(query_dsl)

    def ajustar_aggs(aggs):
        for _agg_name, agg_body in aggs.items():
            for _agg_type, params in agg_body.items():
                if isinstance(params, dict) and "field" in params:
                    field = params["field"]
                    field_type, field_info = get_field_type(mapping, field)
                    if field_type == "text" and has_keyword_subfield(field_info):
                        params["field"] = field + ".keyword"
                # Recursivo para sub-aggs
                if "aggs" in agg_body:
                    ajustar_aggs(agg_body["aggs"])

    if "aggs" in query:
        ajustar_aggs(query["aggs"])
    return query
