from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from CEMIG import *
from anticaptchaofficial.recaptchav2proxyless import recaptchaV2Proxyless
import time
import selenium.common.exceptions

link = "https://atende.cemig.com.br/Login"
servico = Service(ChromeDriverManager().install())
navegador = webdriver.Chrome(service=servico)

try:

    navegador.get(link)

    WebDriverWait(navegador, 10).until(
        EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
    ).click()

    navegador.find_element(By.XPATH, '//*[@id="acesso"]').send_keys(usuario)
    navegador.find_element(By.XPATH, '//*[@id="senha"]').send_keys(senha)
    time.sleep(5)  # Aguardar o carregamento do captcha

    chave_captcha = navegador.find_element(By.CLASS_NAME, 'g-recaptcha').get_attribute('data-sitekey')

    solver = recaptchaV2Proxyless()
    solver.set_verbose(1)
    solver.set_key(api_key)
    solver.set_website_url(link)
    solver.set_website_key(chave_captcha)

    resposta = solver.solve_and_return_solution()

    if resposta != 0:
        print("Captcha resolvido com sucesso:", resposta)
        navegador.execute_script(f"document.getElementById('g-recaptcha-response').innerHTML = '{resposta}'")
        navegador.find_element(By.XPATH, '//*[@id="submitForm"]/div').click()
    else:
        print("Erro ao resolver captcha:", solver.err_string)
        navegador.quit()
        exit()

    def clicar_esperar(xpath, timeout=15):
        while True:
            try:
                WebDriverWait(navegador, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                ).click()
                break
            except (selenium.common.exceptions.ElementClickInterceptedException,
                    selenium.common.exceptions.StaleElementReferenceException):
                time.sleep(1)

    def processar_codigo(codigo):
        print(f"Processando código: {codigo}")
        campo_instalacao = WebDriverWait(navegador, 10).until(
            EC.visibility_of_element_located((By.ID, "limparInst"))
        )
        campo_instalacao.clear()  # Limpa a caixa de entrada antes de inserir o código
        time.sleep(2)  # Pausa para garantir que o campo esteja limpo
        campo_instalacao.send_keys(codigo)

        # Garantir que o código foi inserido corretamente
        for _ in range(3):
            if campo_instalacao.get_attribute('value') == codigo:
                break
            campo_instalacao.clear()
            time.sleep(1)
            campo_instalacao.send_keys(codigo)
            time.sleep(1)
        else:
            raise ValueError(f"Falha ao inserir o código: {codigo}")

        navegador.find_element(By.XPATH, '//*[@id="pesquisaInstalacaoTop"]').click()
        clicar_esperar('//*[@id="divMiniMicroGeracaoDistribuida"]')
        clicar_esperar('//*[@id="divEscolherServico"]/div[2]/div[4]/div/div/button')
        clicar_esperar('//*[@id="dadosSituacaoIN"]/i[2]')
        clicar_esperar('//*[@id="btnSelecionarOutraIN"]')

    for codigo in codigos_gd:
        try:
            processar_codigo(codigo)
            print(f"Código {codigo} processado com sucesso.")
        except Exception as e:
            print(f"Erro ao processar o código {codigo}: {e}")

except Exception as e:
    print("Ocorreu um erro:", str(e))

finally:
    navegador.quit()

