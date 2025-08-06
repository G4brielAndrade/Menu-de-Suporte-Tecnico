#!/usr/bin/env python3
# suporte_menu.py
# Menu de suporte técnico para Windows
# Requer Python 3.6+
# Use com cuidado — alguns comandos exigem privilégios de administrador.

import os
import subprocess
import sys
import shutil
import ctypes
from pathlib import Path
import time

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def run_command(cmd, check=False, shell=True):
    """Executa um comando e mostra saída básica."""
    print(f"\n>> Executando: {cmd}\n")
    try:
        completed = subprocess.run(cmd, shell=shell, check=check)
        print(f"\n>> Código de saída: {completed.returncode}")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar comando: {e}")
    input("\nPressione Enter para continuar...")

# 1. Verificar e Reparar Disco (CHKDSK)
def chkdsk_drive():
    drive = input("Digite a letra da unidade para verificar (ex: C): ").strip().upper()
    if not drive:
        drive = "C"
    cmd = f"chkdsk {drive}: /f /r"
    print("Aviso: chkdsk pode solicitar reinicialização e levar bastante tempo.")
    confirm = input(f"Executar '{cmd}'? (s/N): ").strip().lower()
    if confirm == 's':
        run_command(cmd)

# 2. Reparar Arquivos de Sistema (SFC)
def sfc_scan():
    if not is_admin():
        print("SFC precisa de privilégios de administrador. Execute o script como Administrador.")
        input("Pressione Enter para continuar...")
        return
    cmd = "sfc /scannow"
    run_command(cmd)

# 3. Limpar Arquivos Temporarios e Cache DNS
def limpar_temporarios_e_dns():
    # Limpar %TEMP% e C:\Windows\Temp
    temp_paths = []
    env_temp = os.getenv('TEMP') or os.getenv('TMP')
    if env_temp:
        temp_paths.append(Path(env_temp))
    win_temp = Path(os.getenv('WINDIR', 'C:\\Windows')) / "Temp"
    temp_paths.append(win_temp)

    print("Pastas temporárias que serão limpas:")
    for p in temp_paths:
        print(f" - {p}")
    confirm = input("Continuar e tentar remover arquivos nessas pastas? (s/N): ").strip().lower()
    if confirm == 's':
        for p in temp_paths:
            try:
                if p.exists():
                    for item in p.iterdir():
                        try:
                            if item.is_file() or item.is_symlink():
                                item.unlink()
                            elif item.is_dir():
                                shutil.rmtree(item)
                        except Exception as e:
                            # não interrompe se algum arquivo estiver em uso
                            print(f"Não foi possível remover {item}: {e}")
                    print(f"Limpeza concluída em {p}")
                else:
                    print(f"Pasta não encontrada: {p}")
            except Exception as e:
                print(f"Erro ao limpar {p}: {e}")

    # Flush DNS
    confirm_dns = input("Executar flush do DNS (ipconfig /flushdns)? (s/N): ").strip().lower()
    if confirm_dns == 's':
        run_command("ipconfig /flushdns")

# 4. Diagnóstico de memória (Windows Memory Diagnostic)
def diagnostico_memoria():
    # mdsched.exe -> Windows Memory Diagnostic
    print("O Diagnóstico de Memória do Windows será aberto. Ele pode solicitar reinicialização.")
    confirm = input("Abrir Windows Memory Diagnostic? (s/N): ").strip().lower()
    if confirm == 's':
        run_command("mdsched.exe")

# 5. Verificar Conectividade de Rede (ping/teste)
def verificar_conectividade():
    alvo = input("Digite o host/ip para pingar (padrão: 8.8.8.8): ").strip() or "8.8.8.8"
    run_command(f"ping {alvo} -n 4")

# 6. Gerenciar Processos (Task Manager)
def abrir_task_manager():
    run_command("taskmgr")

# 7. Backup de Drivers (gera lista de drivers com pnputil)
def backup_drivers_list():
    print("Exportando lista de pacotes de driver instalados (pnputil).")
    out = Path.cwd() / "drivers_list.txt"
    try:
        with open(out, "w", encoding="utf-8", errors="ignore") as f:
            subprocess.run("pnputil /enum-drivers", shell=True, stdout=f)
        print(f"Lista salva em: {out}")
    except Exception as e:
        print("Erro ao exportar lista:", e)
    input("Pressione Enter para continuar...")

# 8. Verificar Atualizações de Windows Update (abre a página)
def abrir_windows_update():
    run_command("start ms-settings:windowsupdate")

# 9. Informações do Sistema
def info_sistema():
    run_command("systeminfo")

# 10. Limpar Cache DNS (já incluído, mas disponibilizo separado)
def limpar_cache_dns():
    run_command("ipconfig /flushdns")

# 11. Reiniciar Serviços de Rede
def reiniciar_servicos_rede():
    print("Este procedimento reinicia serviços de rede básicos (ex.: DHCP, DNS Client).")
    confirm = input("Continuar? (s/N): ").strip().lower()
    if confirm == 's':
        run_command("net stop dnscache && net start dnscache")
        run_command("net stop dhcp && net start dhcp")

# 12. Desfragmentar Disco (somente para HDDs)
def desfragmentar_disco():
    unidade = input("Unidade para desfragmentar (ex: C): ").strip().upper() or "C"
    cmd = f"defrag {unidade}: /O"
    run_command(cmd)

# 13. Gerenciar Usuários Locais (abre lusrmgr.msc)
def gerenciar_usuarios_locais():
    run_command("lusrmgr.msc")

# 14. Verificar Integridade (DISM)
def dism_restore():
    if not is_admin():
        print("DISM precisa de privilégios de administrador. Execute o script como Administrador.")
        input("Pressione Enter para continuar...")
        return
    cmd = "DISM /Online /Cleanup-Image /RestoreHealth"
    run_command(cmd, check=True)

# 15. Ativar/Desativar Firewall (exemplo)
def toggle_firewall():
    estado = input("Deseja (a)ativar ou (d)esativar o Firewall do Windows? (a/d): ").strip().lower()
    if estado == 'a':
        run_command("netsh advfirewall set allprofiles state on")
    elif estado == 'd':
        run_command("netsh advfirewall set allprofiles state off")
    else:
        print("Opção inválida.")

# 16. Ver logs de eventos (Event Viewer)
def ver_logs_eventos():
    run_command("eventvwr.msc")

# 17. Testar velocidade (usa powershell - simples)
def testar_velocidade():
    print("Irá abrir um comando PowerShell para testar uma requisição simples (não é um teste de banda completo).")
    run_command("powershell -Command \"Invoke-WebRequest -Uri 'https://www.google.com' -UseBasicParsing | Select-Object StatusCode\"")

# 18. Criar Ponto de Restauração (requer admin)
def criar_ponto_restauracao():
    if not is_admin():
        print("Criar ponto de restauração precisa de privilégios de administrador.")
        input("Pressione Enter para continuar...")
        return
    nome = input("Nome do ponto de restauração: ").strip() or f"Ponto_{int(time.time())}"
    cmd = f"powershell -Command \"Checkpoint-Computer -Description '{nome}' -RestorePointType 'MODIFY_SETTINGS'\""
    run_command(cmd)

# 19. Executar Comando Personalizado (CMD)
def comando_personalizado():
    cmd = input("Digite o comando a ser executado: ").strip()
    if cmd:
        run_command(cmd)

# 20. Atualizar todos os programas via Winget
def atualizar_via_winget():
    if not is_admin():
        print("Winget pode precisar de privilégios de administrador dependendo do app.")
        confirm = input("Continuar mesmo sem privilégios administrativos? (s/N): ").strip().lower()
        if confirm != 's':
            return
    print("Executando: winget upgrade --all")
    run_command("winget upgrade --all")

# 21. Abrir ferramentas do sistema (lista)
def abrir_ferramentas():
    tools = {
        "1": ("Gerenciador de Dispositivos", "devmgmt.msc"),
        "2": ("Visualizador de Eventos", "eventvwr.msc"),
        "3": ("Gerenciamento do Computador", "compmgmt.msc"),
        "4": ("Painel de Controle (Programas)", "appwiz.cpl"),
        "5": ("Propriedades do Sistema", "sysdm.cpl"),
        "6": ("Prompt de Comando (Admin)", "cmd"),
        "7": ("PowerShell (Admin)", "powershell")
    }
    print("Ferramentas disponíveis:")
    for k,v in tools.items():
        print(f"{k}. {v[0]}")
    escolha = input("Escolha (número) ou Enter para voltar: ").strip()
    if escolha in tools:
        run_command(tools[escolha][1])

def sair():
    print("Saindo...")
    sys.exit(0)

MENU_OPTIONS = {
    "1": ("Verificar e Reparar Disco (CHKDSK)", chkdsk_drive),
    "2": ("Reparar Arquivos de Sistema (SFC)", sfc_scan),
    "3": ("Limpar Arquivos Temporários e Cache DNS", limpar_temporarios_e_dns),
    "4": ("Diagnóstico de Memória", diagnostico_memoria),
    "5": ("Verificar Conectividade de Rede (Ping)", verificar_conectividade),
    "6": ("Abrir Task Manager", abrir_task_manager),
    "7": ("Backup de Drivers (lista)", backup_drivers_list),
    "8": ("Abrir Windows Update", abrir_windows_update),
    "9": ("Informações do Sistema", info_sistema),
    "10": ("Limpar Cache DNS", limpar_cache_dns),
    "11": ("Reiniciar Serviços de Rede", reiniciar_servicos_rede),
    "12": ("Desfragmentar Disco", desfragmentar_disco),
    "13": ("Gerenciar Usuários Locais", gerenciar_usuarios_locais),
    "14": ("Verificar Integridade (DISM)", dism_restore),
    "15": ("Ativar/Desativar Firewall do Windows", toggle_firewall),
    "16": ("Ver Logs de Eventos", ver_logs_eventos),
    "17": ("Testar Velocidade Básica", testar_velocidade),
    "18": ("Criar Ponto de Restauração", criar_ponto_restauracao),
    "19": ("Executar Comando Personalizado (CMD)", comando_personalizado),
    "20": ("Atualizar Todos os Programas via Winget", atualizar_via_winget),
    "21": ("Abrir Ferramentas do Sistema", abrir_ferramentas),
    "22": ("Sair", sair),
}

def print_menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("="*50)
    print(" MENU DE SUPORTE TÉCNICO T.I- Script Python")
    print(" por: Gabriel Andrade - v1.0")
    print("="*50)
    for key in sorted(MENU_OPTIONS.keys(), key=lambda k: int(k)):
        print(f"{key}. {MENU_OPTIONS[key][0]}")
    print("="*50)

def main():
    while True:
        print_menu()
        escolha = input("Escolha uma opção (1-22): ").strip()
        action = MENU_OPTIONS.get(escolha)
        if action:
            try:
                action[1]()
            except Exception as e:
                print("Erro durante execução:", e)
                input("Pressione Enter para continuar...")
        else:
            print("Opção inválida. Tente novamente.")
            time.sleep(1)

if __name__ == "__main__":
    main()
