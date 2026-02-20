#!/usr/bin/python3
import socket
import sys
import re
import os

# --- 1. DEFINIÇÃO DE CORES (Corrigindo o NameError) ---
AZUL = "\033[94m"
VERDE = "\033[92m"
AMARELO = "\033[93m"
VERMELHO = "\033[91m"
ROXO = "\033[95m"
BRANCO = "\033[97m"
INFO = "\033[94m" 
RESET = "\033[0m"

# --- 2. BANNER CORRIGIDO (Prefixo 'fr' evita o SyntaxWarning) ---
WHOIS_ART = fr"""
{AZUL} _    _ _     _           _     {RESET}
{AZUL}| |  | (_)___(_) ___  ___| |___ {RESET}
{AZUL}| |  | | / __| |/ _ \/ __| / __|{RESET}
{AZUL}| |__| | \__ \ |  __/ (__| \__ \{RESET}
{AZUL} \____/|_|___/_|\___|\___|_|___/{RESET}
{ROXO}       :: Ferramenta de Consulta WHOIS ::{RESET}
{ROXO}       Desenvolvido por ghostcricket{RESET}
------------------------------------------
"""

def salvar_resultado(dominio, conteudo):
    """Salva o resultado da consulta em um arquivo .txt na pasta atual."""
    nome_arquivo = f"whois_{dominio}.txt"
    try:
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            f.write(conteudo)
        print(f"{VERDE}[+] Resultado salvo com sucesso em: {nome_arquivo}{RESET}")
    except Exception as e:
        print(f"{VERMELHO}[!] Erro ao salvar arquivo: {e}{RESET}")

def buscar_whois_server(dominio_limpo):
    """Consulta a IANA para encontrar o servidor WHOIS de referência."""
    print(f"{INFO}[+] Buscando servidor WHOIS para {dominio_limpo}...{RESET}")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect(("whois.iana.org", 43))
        s.send((dominio_limpo + "\r\n").encode())
        
        resposta = s.recv(4096).decode('latin-1')
        s.close()

        match = re.search(r'(?:whois|refer):\s*([a-zA-Z0-9.-]+)', resposta)
        if match:
            return match.group(1)
        return "whois.verisign-grs.com" 
    except Exception as e:
        print(f"{VERMELHO}[!] Erro na conexão IANA: {e}{RESET}")
        return None

def realizar_consulta(dominio_limpo, server):
    """Consulta o servidor específico e retorna a resposta completa."""
    print(f"{INFO}[+] Conectando ao servidor específico: {server}{RESET}")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((server, 43))
        s.send((dominio_limpo + "\r\n").encode())
        
        dados_completos = b""
        while True:
            bloco = s.recv(4096)
            if not bloco: break
            dados_completos += bloco
            
        s.close()
        return dados_completos.decode('latin-1', errors='ignore')
    except Exception as e:
        return f"Erro na consulta final: {e}"

def main():
    print(WHOIS_ART)
    
    if len(sys.argv) > 1:
        alvo = sys.argv[1]
    else:
        print(f"{AMARELO}[*] Modo Interativo ativado. Digite 'sair' para parar.{RESET}")
        alvo = input(f"{BRANCO}>> Digite o domínio (ex: google.com): {RESET}").strip()

    if not alvo or alvo.lower() == 'sair':
        print(f"{INFO}Saindo...{RESET}")
        sys.exit()

    # Remove http://, https:// e barras finais para evitar erros de socket
    alvo_limpo = re.sub(r'^https?://|/.*$', '', alvo)

    srv = buscar_whois_server(alvo_limpo)
    if srv:
        resultado = realizar_consulta(alvo_limpo, srv)
        print(f"\n{VERDE}--- RESULTADO ENCONTRADO ---{RESET}")
        print(f"{BRANCO}{resultado}{RESET}")
        print(f"{VERDE}----------------------------{RESET}")
        
        # Salva o arquivo automaticamente
        salvar_resultado(alvo_limpo, resultado)

if __name__ == "__main__":
    main()