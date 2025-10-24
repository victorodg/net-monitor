# net-monitor
A small network sniffer application

# Monitor de Rede Simplificado

Um monitor de tráfego de rede minimalista inspirado no **nethogs**, que mostra em tempo real quais aplicações estão enviando dados, para onde e quanto.

## 🎯 O que faz

Esta aplicação monitora todas as conexões de rede ativas no seu sistema e exibe:

- **Aplicação**: Nome do processo que está enviando dados
- **Socket Local**: Endereço IP e porta de origem (seu computador)
- **Servidor Destino**: Para onde os dados estão sendo enviados (com resolução DNS quando possível)
- **Protocolo**: TCP ou UDP
- **Dados Enviados**: Quantidade de dados transmitidos

## ✨ Características

- **Histórico Visual**: Mantém as últimas 5 atualizações visíveis na tela
- **Atualização a cada 10 segundos**: Com contador regressivo em tempo real
- **Resolução DNS**: Converte IPs para nomes de domínio legíveis (ex: `google.com` ao invés de `142.250.185.46`)
- **Colunas Dinâmicas**: Ajusta automaticamente a largura das colunas para acomodar endereços IPv6 longos
- **Código Comentado**: Todo o código possui comentários explicativos em português brasileiro

## 📋 Requisitos

- Python 3.6 ou superior
- Biblioteca `psutil`
- Linux/Unix (requer privilégios de root para ver todas as conexões)

## 🚀 Instalação

1. **Clone ou baixe o arquivo `net_monitor.py`**

2. **Instale a dependência:**
   ```bash
   pip install psutil
   ```

## 💻 Como Usar

**Execute com privilégios de root/sudo:**
```bash
sudo python3 net_monitor.py
```

**Para interromper o monitoramento:**
- Pressione `Ctrl+C`

## 📊 Exemplo de Saída

```
Monitor de Rede - Histórico das Últimas 5 Atualizações
Pressione Ctrl+C para sair
========================================================

[Atualização #1 - 14:23:10]
APLICAÇÃO            | SOCKET LOCAL              | SERVIDOR DESTINO          | PROTO  | DADOS
---------------------------------------------------------------------------------------------
firefox              | 192.168.1.100:54321       | google.com:443            | TCP    | 15.42 KB
chrome               | 192.168.1.100:54322       | youtube.com:443           | TCP    | 8.21 MB
spotify              | 192.168.1.100:54323       | audio-ak.spotify.com:443  | TCP    | 2.15 MB

[Atualização #2 - 14:23:20]
APLICAÇÃO            | SOCKET LOCAL              | SERVIDOR DESTINO          | PROTO  | DADOS
---------------------------------------------------------------------------------------------
firefox              | 192.168.1.100:54321       | google.com:443            | TCP    | 22.18 KB
...

Próxima atualização em 10 segundos...
```

## ⚙️ Como Funciona

1. **Coleta de Conexões**: Usa `psutil.net_connections()` para listar todas as conexões ativas
2. **Identificação de Processos**: Relaciona cada conexão ao processo (PID) responsável
3. **Medição de Dados**: Calcula a diferença de bytes escritos entre atualizações
4. **Resolução DNS**: Tenta converter IPs para nomes de domínio usando DNS reverso
5. **Cache**: Armazena resultados de DNS para melhorar performance
6. **Histórico**: Mantém as últimas 5 atualizações em memória usando `deque`

## 🔒 Permissões

O programa precisa de privilégios elevados (root/sudo) porque:
- Acessa informações de processos de outros usuários
- Lê estatísticas de rede do kernel
- Monitora conexões de todo o sistema

## ⚠️ Limitações

- **Aproximação de dados**: Os bytes medidos são do processo inteiro, não apenas da conexão específica
- **Sem histórico persistente**: Os dados são perdidos ao fechar o programa
- **DNS reverso pode falhar**: Alguns IPs não possuem registro reverso e aparecerão como números
- **Requer root**: Sem privilégios elevados, mostra apenas processos do usuário atual

## 🛠️ Tecnologias Utilizadas

- **Python 3**: Linguagem principal
- **psutil**: Biblioteca para informações de sistema e processos
- **socket**: Módulo nativo para resolução DNS
- **collections.deque**: Estrutura de dados para histórico com tamanho fixo

## 📝 Notas

- O intervalo de atualização pode ser modificado alterando o valor no loop principal (padrão: 10 segundos)
- O tamanho do histórico pode ser ajustado mudando `maxlen=5` no `deque`
- Para monitorar apenas IPv4 ou IPv6, modifique o parâmetro `kind` em `net_connections()`

## 📄 Licença

Este código é fornecido como está, para fins educacionais e de monitoramento pessoal.

---

**Desenvolvido com ❤️ para monitoramento de rede simplificado**
