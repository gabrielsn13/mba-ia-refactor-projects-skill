# Template do Relatório de Auditoria (Fase 2)

Use **exatamente** esta estrutura. Substitua os placeholders `<...>`. Findings ordenados **CRITICAL → HIGH → MEDIUM → LOW**. Numere os findings sequencialmente.

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome da pasta do projeto>
Stack:   <linguagem> + <framework>
Files:   <N> analyzed | ~<L> lines of code

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

## Findings

### [CRITICAL] <Nome do anti-pattern (ID do catálogo)>
File: <caminho>:<linha-inicial>-<linha-final>   (múltiplos: <arq1>:<l1-l2>, <arq2>:<l3>)
Description: <o que foi encontrado, citando o trecho/identificador real>
Impact: <consequência concreta para segurança, manutenção, testes ou performance>
Recommendation: <correção específica, referenciando o padrão do playbook>

### [HIGH] ...

### [MEDIUM] ...

### [LOW] ...

## Deprecated APIs
<lista "arquivo:linha — API obsoleta → equivalente moderno" ou "None detected">

================================
Total: <N> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

## Regras de preenchimento

1. **File** deve conter caminho relativo à raiz do projeto e linhas exatas verificadas no código. Nunca use "várias linhas" ou intervalos estimados.
2. O **Summary** deve bater com a quantidade de findings listados; o **Total** é a soma.
3. Findings de APIs deprecated entram também na lista de findings (severidade LOW/MEDIUM) e são repetidos de forma resumida na seção "Deprecated APIs".
4. Mínimo esperado: 5 findings com pelo menos 1 CRITICAL ou HIGH; não crie findings sem evidência para atingir o número.
5. Escreva descrições em português, citando nomes reais (funções, variáveis, rotas).
6. A última linha do relatório impresso deve ser a pergunta de confirmação. Ao salvar o arquivo em `reports/`, **omita** essa pergunta final.
