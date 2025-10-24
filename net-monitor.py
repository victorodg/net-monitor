#!/usr/bin/env python3
"""
Monitor de Rede Simplificado - Similar ao nethogs
Mostra: Aplicação | Servidor Destino | Dados Enviados
Mantém histórico das últimas 5 atualizações
"""

import psutil
import time
import os
import socket
from collections import defaultdict, deque
from datetime import datetime

# Dicionário para armazenar estatísticas anteriores de cada conexão
# Chave: (pid, endereço_remoto), Valor: bytes enviados anteriormente
stats_anteriores = defaultdict(int)

# Cache de DNS reverso para evitar consultas repetidas
# Chave: IP, Valor: hostname ou None se falhou
cache_dns = {}

# Fila para manter as últimas 5 atualizações (FIFO - First In First Out)
# Cada elemento é uma tupla: (timestamp, lista_de_conexões)
historico_atualizacoes = deque(maxlen=5)

def truncar_texto(texto, tamanho_max):
    """Trunca texto longo adicionando '...' no final se necessário"""
    if len(texto) <= tamanho_max:
        return texto
    return texto[:tamanho_max-3] + "..."

def obter_hostname(ip):
    """Tenta converter IP para hostname legível usando DNS reverso"""
    # Verifica se já está no cache
    if ip in cache_dns:
        # Se o valor em cache é None, retorna o IP original
        return ip if cache_dns[ip] is None else cache_dns[ip]
    
    try:
        # Tenta fazer DNS reverso com timeout curto (0.5 segundos)
        hostname = socket.gethostbyaddr(ip)[0]
        # Remove "www." do início se existir para ficar mais limpo
        if hostname.startswith('www.'):
            hostname = hostname[4:]
        cache_dns[ip] = hostname
        return hostname
    except (socket.herror, socket.gaierror, socket.timeout):
        # Se falhar, armazena None no cache e retorna o IP original
        cache_dns[ip] = None
        return ip

def formatar_bytes(bytes):
    """Converte bytes para formato legível (KB, MB, etc)"""
    for unidade in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unidade}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"

def obter_nome_processo(pid):
    """Obtém o nome do processo a partir do PID"""
    try:
        proc = psutil.Process(pid)
        return proc.name()
    except:
        return "Desconhecido"

def coletar_dados_rede():
    """Coleta dados de conexões de rede ativas e retorna uma lista formatada"""
    # Dicionário para acumular dados por (processo, servidor, socket_local, protocolo)
    # Chave: (nome_processo, endereço_remoto, socket_local, protocolo), Valor: bytes enviados
    dados_atuais = defaultdict(int)
    
    # Percorre todas as conexões de rede ativas
    for conn in psutil.net_connections(kind='inet'):
        # Ignora conexões sem endereço remoto (não estão enviando para servidor)
        if not conn.raddr:
            continue
            
        # Ignora conexões sem PID (sistema)
        if not conn.pid:
            continue
        
        # Obtém o endereço remoto (servidor) no formato IP:PORTA
        ip_destino = conn.raddr.ip
        porta_destino = conn.raddr.port
        
        # Tenta obter um hostname legível para o IP de destino
        hostname = obter_hostname(ip_destino)
        servidor = f"{hostname}:{porta_destino}"
        
        # Obtém o socket local (IP:PORTA de origem)
        socket_local = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A"
        
        # Obtém o tipo de protocolo (TCP, UDP, etc)
        # conn.type retorna um inteiro, convertemos para nome legível
        if conn.type == 1:  # SOCK_STREAM
            protocolo = "TCP"
        elif conn.type == 2:  # SOCK_DGRAM
            protocolo = "UDP"
        else:
            protocolo = f"Tipo-{conn.type}"
        
        # Obtém o nome da aplicação
        app = obter_nome_processo(conn.pid)
        
        # Cria uma chave única para esta conexão
        chave_conn = (conn.pid, servidor, socket_local)
        chave_display = (app, servidor, socket_local, protocolo)
        
        # Tenta obter estatísticas de IO do processo
        try:
            proc = psutil.Process(conn.pid)
            io = proc.io_counters()
            bytes_enviados = io.write_bytes  # Total de bytes escritos pelo processo
            
            # Calcula a diferença desde a última verificação
            bytes_diff = bytes_enviados - stats_anteriores[chave_conn]
            
            # Atualiza o valor anterior
            stats_anteriores[chave_conn] = bytes_enviados
            
            # Acumula os dados para esta combinação processo-servidor-socket-protocolo
            if bytes_diff > 0:
                dados_atuais[chave_display] += bytes_diff
                
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Processo terminou ou sem permissão
            continue
    
    # Retorna lista ordenada por quantidade de dados (maior para menor)
    return sorted(dados_atuais.items(), key=lambda x: x[1], reverse=True)

def exibir_historico():
    """Exibe o histórico completo das últimas 5 atualizações"""
    # Limpa a tela
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print("Monitor de Rede - Histórico das Últimas 5 Atualizações")
    print("Pressione Ctrl+C para sair")
    
    # Se não houver histórico ainda
    if not historico_atualizacoes:
        print("="*120)
        print("Aguardando primeira atualização...")
        return
    
    # Calcula o tamanho máximo necessário para cada coluna em todos os dados
    tam_app = 20  # Tamanho mínimo
    tam_socket = 25  # Tamanho mínimo
    tam_servidor = 25  # Tamanho mínimo
    
    # Percorre todo o histórico para encontrar o texto mais longo de cada coluna
    for timestamp, dados in historico_atualizacoes:
        for (app, servidor, socket_local, protocolo), bytes_enviados in dados:
            tam_app = max(tam_app, len(app))
            tam_socket = max(tam_socket, len(socket_local))
            tam_servidor = max(tam_servidor, len(servidor))
    
    # Calcula largura total da linha
    largura_total = tam_app + tam_socket + tam_servidor + 6 + 12 + 13  # +13 para separadores " | "
    
    print("="*largura_total)
    
    # Exibe cada atualização do histórico
    for idx, (timestamp, dados) in enumerate(historico_atualizacoes, 1):
        print(f"\n[Atualização #{idx} - {timestamp}]")
        print(f"{'APLICAÇÃO':<{tam_app}} | {'SOCKET LOCAL':<{tam_socket}} | {'SERVIDOR DESTINO':<{tam_servidor}} | {'PROTO':<6} | {'DADOS':<12}")
        print("-"*largura_total)
        
        # Se houve atividade nesta atualização
        if dados:
            for (app, servidor, socket_local, protocolo), bytes_enviados in dados:
                print(f"{app:<{tam_app}} | {socket_local:<{tam_socket}} | {servidor:<{tam_servidor}} | {protocolo:<6} | {formatar_bytes(bytes_enviados):<12}")
        else:
            print("Nenhuma atividade de rede detectada neste período")
    
    print("\n" + "="*largura_total)
    # Mensagem removida - o contador regressivo será exibido na função main()

def main():
    """Função principal - loop de monitoramento"""
    print("Monitor de Rede - Iniciando...")
    print("NOTA: Execute como root/sudo para ver todos os processos")
    
    # Verifica se está rodando como root
    if os.geteuid() != 0:
        print("AVISO: Rodando sem privilégios root. Algumas conexões podem não aparecer.")
    
    time.sleep(2)  # Pausa para o usuário ler as mensagens
    
    try:
        # Loop infinito - atualiza a cada 10 segundos
        while True:
            # Obtém timestamp atual formatado
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Coleta os dados de rede
            dados = coletar_dados_rede()
            
            # Adiciona ao histórico (automáticamente remove o mais antigo se já tiver 5)
            historico_atualizacoes.append((timestamp, dados))
            
            # Exibe o histórico completo
            exibir_historico()
            
            # Contador regressivo de 10 segundos com atualização a cada segundo
            for segundos_restantes in range(10, 0, -1):
                # Move o cursor para o início da linha e sobrescreve
                print(f"\rPróxima atualização em {segundos_restantes} segundos...  ", end='', flush=True)
                time.sleep(1)
            
            # Quebra de linha após o countdown terminar
            print()
            
    except KeyboardInterrupt:
        # Usuário pressionou Ctrl+C
        print("\n\nMonitoramento encerrado.")

# Ponto de entrada do programa
if __name__ == "__main__":
    main()