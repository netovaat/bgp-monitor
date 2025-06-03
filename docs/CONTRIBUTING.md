# Contribuindo para o BGP Monitor

Obrigado por considerar contribuir para o BGP Monitor! Este documento fornece diretrizes para contribuições.

## 🚀 Como Contribuir

### 1. Reportar Problemas

- Use o [GitHub Issues](https://github.com/seu-usuario/bgp-monitor/issues)
- Descreva o problema claramente
- Inclua informações do sistema (SO, versão Python, etc.)
- Forneça logs relevantes
- Siga o template de issue (se disponível)

### 2. Sugerir Melhorias

- Abra uma issue com label "enhancement"
- Descreva a funcionalidade desejada
- Explique o caso de uso
- Considere a compatibilidade com a arquitetura simplificada

### 3. Enviar Código

#### Processo de Desenvolvimento

1. **Fork** do repositório
2. **Clone** seu fork localmente
3. **Crie** uma branch para sua feature
4. **Desenvolva** e teste localmente
5. **Commit** suas mudanças
6. **Push** para seu fork
7. **Abra** um Pull Request

#### Comandos Básicos

```bash
# Fork e clone
git clone https://github.com/seu-usuario/bgp-monitor.git
cd bgp-monitor

# Criar branch
git checkout -b feature/nova-funcionalidade

# Instalar dependências de desenvolvimento
pip install -r requirements.txt

# Fazer mudanças...

# Commit
git add .
git commit -m "feat: adiciona nova funcionalidade"

# Push
git push origin feature/nova-funcionalidade
```

## 📋 Diretrizes de Desenvolvimento

### Padrões de Código

1. **Python Style Guide**: Siga PEP 8
2. **Imports**: Organize imports (stdlib, third-party, local)
3. **Docstrings**: Use docstrings para funções públicas
4. **Type Hints**: Use type hints quando possível
5. **Error Handling**: Trate erros apropriadamente

#### Exemplo de Código

```python
from typing import Optional, Dict, Any
import asyncio
import httpx

async def fetch_data(url: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
    """
    Busca dados de uma URL.
    
    Args:
        url: URL para fazer requisição
        timeout: Timeout em segundos
        
    Returns:
        Dados JSON ou None se falhar
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        print(f"Erro HTTP: {e}")
        return None
```

### Estrutura de Commits

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Mudanças na documentação
- `style:` Mudanças de formatação
- `refactor:` Refatoração de código
- `test:` Adição/modificação de testes
- `chore:` Tarefas de manutenção

#### Exemplos

```bash
feat: adiciona validação IRR para prefixos
fix: corrige timeout na API do RIPE
docs: atualiza guia de instalação
refactor: simplifica lógica de cache
```

### Testes

1. **Teste** suas mudanças localmente
2. **Verifique** se não quebra funcionalidades existentes
3. **Adicione testes** para novas funcionalidades (se aplicável)
4. **Execute** todos os testes antes do commit

```bash
# Testar aplicação localmente
python app/main.py

# Verificar API
curl http://localhost:8000/health

# Testar funcionalidades específicas
./bgp-monitor.sh status
```

## 🏗️ Arquitetura do Projeto

### Princípios de Design

1. **Simplicidade**: Mantenha o código simples e legível
2. **Modularidade**: Separe responsabilidades em módulos
3. **Configurabilidade**: Use variáveis de ambiente
4. **Robustez**: Trate erros e falhas graciosamente
5. **Performance**: Considere performance, mas priorize simplicidade

### Estrutura de Diretórios

```
bgp-monitor/
├── app/                 # Código principal da aplicação
│   ├── api/            # Endpoints da API REST
│   ├── core/           # Configurações e utilitários
│   ├── services/       # Lógica de negócio
│   └── utils/          # Funções auxiliares
├── docs/               # Documentação
├── requirements.txt    # Dependências Python
└── *.sh               # Scripts de execução
```

### Boas Práticas

1. **Não adicione** dependências desnecessárias
2. **Mantenha** compatibilidade com Python 3.8+
3. **Use** async/await para operações I/O
4. **Implemente** timeout para requisições HTTP
5. **Cache** dados quando apropriado
6. **Log** informações importantes
7. **Documente** funcionalidades novas

## 🧪 Testando Mudanças

### Testes Manuais

```bash
# 1. Iniciar aplicação
./run.sh

# 2. Verificar saúde
curl http://localhost:8000/health

# 3. Adicionar prefixo
./bgp-monitor.sh add-prefix 192.168.1.0/24 "Teste"

# 4. Listar prefixos
./bgp-monitor.sh list-prefixes

# 5. Verificar manualmente
curl -X POST http://localhost:8000/api/v1/prefixes/192.168.1.0%2F24/check

# 6. Verificar métricas
curl http://localhost:8000/metrics
```

### Cenários de Teste

1. **Funcionalidade básica**: Adicionar/remover prefixos
2. **API REST**: Todos os endpoints funcionando
3. **Scheduler**: Verificações automáticas
4. **Notificações**: Telegram funcionando
5. **Resiliência**: Falhas de rede/API
6. **Performance**: Múltiplos prefixos

## 📝 Documentação

### Atualizando Documentação

1. **README.md**: Funcionalidades principais
2. **docs/**: Documentação técnica detalhada
3. **Código**: Docstrings e comentários
4. **API**: Swagger/OpenAPI atualizado

### Formato da Documentação

- Use **Markdown** para documentos
- Inclua **exemplos práticos**
- Mantenha **consistência** de formato
- Adicione **índices** quando necessário

## 🤝 Revisão de Código

### Checklist para Pull Requests

- [ ] Código segue padrões estabelecidos
- [ ] Funcionalidade testada localmente
- [ ] Documentação atualizada (se necessário)
- [ ] Commits seguem padrão conventional
- [ ] Não quebra funcionalidades existentes
- [ ] Performance considerada
- [ ] Logs/erros tratados adequadamente

### Processo de Revisão

1. **Automated checks**: CI/CD (se configurado)
2. **Code review**: Revisão por mantenedores
3. **Testing**: Teste em ambiente local
4. **Merge**: Aprovação e merge

## 📞 Comunicação

- **Issues**: Para bugs e sugestões
- **Discussions**: Para discussões gerais
- **Pull Requests**: Para revisão de código
- **Email**: Para questões privadas (se disponível)

## 🏷️ Versionamento

O projeto segue [Semantic Versioning](https://semver.org/):

- **MAJOR**: Mudanças incompatíveis
- **MINOR**: Novas funcionalidades compatíveis
- **PATCH**: Correções de bugs compatíveis

Exemplo: `1.0.0` → `1.1.0` (nova feature) → `1.1.1` (bugfix)

---

Obrigado por contribuir! Sua ajuda torna o BGP Monitor melhor para todos. 🎉
