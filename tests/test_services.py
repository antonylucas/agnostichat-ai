"""Testes para os módulos de serviço do AgnostiChat."""

from __future__ import annotations

from agnostichat.services.prompt_builder import describe_mapping, montar_prompt
from agnostichat.services.query_utils import ajustar_query_keyword, get_field_type, has_keyword_subfield
from agnostichat.ui.chat import extrair_json, montar_prompt_interpretacao, obter_sugestoes

# ====== extrair_json ======


class TestExtrairJson:
    """Testes para a função extrair_json."""

    def test_extrai_json_de_bloco_markdown(self) -> None:
        texto = '```json\n{"size": 10}\n```'
        assert extrair_json(texto) == '{"size": 10}'

    def test_extrai_json_puro(self) -> None:
        texto = '{"query": {"match_all": {}}}'
        assert extrair_json(texto) == '{"query": {"match_all": {}}}'

    def test_extrai_json_com_texto_extra(self) -> None:
        texto = 'Aqui está a query:\n{"size": 5}\nFim.'
        resultado = extrair_json(texto)
        assert '"size": 5' in resultado


# ====== obter_sugestoes ======


class TestObterSugestoes:
    """Testes para a função obter_sugestoes."""

    def test_retorna_lista_vazia_sem_indice(self) -> None:
        assert obter_sugestoes(None) == []

    def test_retorna_sugestoes_com_indice(self) -> None:
        sugestoes = obter_sugestoes("meu_indice")
        assert len(sugestoes) == 4
        assert all("meu_indice" in s for s in sugestoes)


# ====== describe_mapping ======


class TestDescribeMapping:
    """Testes para a função describe_mapping."""

    def test_mapping_simples(self) -> None:
        mapping = {"properties": {"nome": {"type": "text"}, "idade": {"type": "integer"}}}
        resultado = describe_mapping(mapping)
        assert "nome: text" in resultado
        assert "idade: integer" in resultado

    def test_mapping_aninhado(self) -> None:
        mapping = {
            "properties": {
                "endereco": {
                    "properties": {
                        "rua": {"type": "text"},
                        "cidade": {"type": "keyword"},
                    }
                }
            }
        }
        resultado = describe_mapping(mapping)
        assert "endereco" in resultado
        assert "rua" in resultado


# ====== get_field_type ======


class TestGetFieldType:
    """Testes para a função get_field_type."""

    def test_campo_existente(self) -> None:
        mapping = {"properties": {"nome": {"type": "text"}}}
        tipo, _info = get_field_type(mapping, "nome")
        assert tipo == "text"

    def test_campo_inexistente(self) -> None:
        mapping = {"properties": {"nome": {"type": "text"}}}
        tipo, _info = get_field_type(mapping, "nao_existe")
        assert tipo is None


# ====== has_keyword_subfield ======


class TestHasKeywordSubfield:
    """Testes para a função has_keyword_subfield."""

    def test_com_keyword(self) -> None:
        info = {"type": "text", "fields": {"keyword": {"type": "keyword"}}}
        assert has_keyword_subfield(info) is True

    def test_sem_keyword(self) -> None:
        info = {"type": "text"}
        assert has_keyword_subfield(info) is False

    def test_campo_none(self) -> None:
        assert has_keyword_subfield(None) is False


# ====== ajustar_query_keyword ======


class TestAjustarQueryKeyword:
    """Testes para a função ajustar_query_keyword."""

    def test_ajusta_campo_text_com_keyword(self) -> None:
        mapping = {"properties": {"nome": {"type": "text", "fields": {"keyword": {"type": "keyword"}}}}}
        query = {"aggs": {"nomes": {"terms": {"field": "nome"}}}}
        resultado = ajustar_query_keyword(query, mapping)
        assert resultado["aggs"]["nomes"]["terms"]["field"] == "nome.keyword"

    def test_nao_altera_campo_sem_keyword(self) -> None:
        mapping = {"properties": {"idade": {"type": "integer"}}}
        query = {"aggs": {"idades": {"terms": {"field": "idade"}}}}
        resultado = ajustar_query_keyword(query, mapping)
        assert resultado["aggs"]["idades"]["terms"]["field"] == "idade"

    def test_query_sem_aggs(self) -> None:
        mapping = {"properties": {"nome": {"type": "text"}}}
        query = {"query": {"match_all": {}}}
        resultado = ajustar_query_keyword(query, mapping)
        assert resultado == {"query": {"match_all": {}}}


# ====== montar_prompt ======


class TestMontarPrompt:
    """Testes para a função montar_prompt."""

    def test_prompt_contem_elementos_essenciais(self) -> None:
        mapping = {"properties": {"nome": {"type": "text"}}}
        amostras = [{"nome": "Teste"}]
        prompt = montar_prompt("meu_indice", mapping, None, None, amostras, "Quantos documentos?")
        assert "meu_indice" in prompt
        assert "nome: text" in prompt
        assert "Quantos documentos?" in prompt
        assert "Teste" in prompt


# ====== montar_prompt_interpretacao ======


class TestMontarPromptInterpretacao:
    """Testes para a função montar_prompt_interpretacao."""

    def test_com_aggs_e_hits(self) -> None:
        resultado = {
            "aggregations": {"total": {"value": 100}},
            "hits": {"hits": [{"_source": {"nome": "Teste"}}]},
        }
        prompt = montar_prompt_interpretacao("Pergunta?", '{"size": 0}', resultado, True, True)
        assert "Pergunta?" in prompt
        assert "agregação" in prompt.lower() or "Resultado" in prompt

    def test_sem_resultados(self) -> None:
        resultado = {}
        prompt = montar_prompt_interpretacao("Pergunta?", '{"size": 0}', resultado, False, False)
        assert "Nenhum resultado" in prompt
