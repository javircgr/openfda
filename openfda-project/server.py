import http.server
import http.client
import json
import socketserver

Puerto = 8000
class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    OPENFDA_URL = "api.fda.gov"
    OPENFDA_EVENTO = "/drug/label.json"
    OPENFDA_DROGA = '&search=active_ingredient:'
    OPENFDA_COMPANIA = '&search=openfda.manufacturer_name:'


    def formulario(self):
        html = """
            <html>
                <head>
                    <title>Aplicacion OpenFDA</title>
                </head>
                <body style='background-color: #46A1FD;'>
                    <h1>Buscador OpenFDA. </h1>
                    <h4>* Para obtener un medicamento por defecto, pulsa 'Lista Medicamentos'</h4>
                    <form method="get" action="listDrugs">
                        Inserte cantidad para obtener mas de uno:
                        <br><input name="limit" type="text">
                        <input type = "submit" value="Lista Medicamentos"><br>
                        </input>
                    </form>
                   <h4>* Busqueda de medicamento en concreto: </h4>
                    <form method="get" action="searchDrug">
                        <input type = "submit" value="Buscar">
                        <input type = "text" name="drug"></input>
                        </input>
                    </form>
                    <h4>* Para obtener una empresa por defecto, pulsa 'Lista Empresas'</h4>
                    <form method="get" action="listCompanies">
                        Inserte cantidad para obtener mas de uno:
                        <br><input name="limit" type="text">
                        <input type = "submit" value="Lista Empresas"><br>
                        </input>
                    </form>
                    <h4>* Busqueda de empresa en concreto: </h4>
                    <form method="get" action="searchCompany">
                        <input type = "submit" value="Buscar">
                        <input type = "text" name="company"></input>
                        </input>
                    </form>
                    <h4>*Advertencias*</h4>
                    <form method="get" action="listWarnings">
                        Inserte cantidad para obtener mas de una advertencia:
                        <br><input name="limit" type="text">
                        <input type = "submit" value="Lista Advertencias"><br>
                        </input>
                    </form>
                </body>
            </html>
                """
        return html

    def obtener_resultados (self, limit=10):
        headers = {'User-Agent': 'http-client'}
        conexion = http.client.HTTPSConnection(self.OPENFDA_URL)
        conexion.request("GET", self.OPENFDA_EVENTO + "?limit="+str(limit))
        print (self.OPENFDA_EVENTO + "?limit="+str(limit))
        c1 = conexion.getresponse()
        info_raw = c1.read().decode("utf8")
        informacion = json.loads(info_raw)
        resultados_obtenidos = informacion['results']
        return resultados_obtenidos

    def pagina_web (self, lista):
        lista_html = """
                                <html>
                                    <head>
                                        <title>Aplicacion de OpenFDA</title>
                                    </head>
                                    <body style='background-color: #4AFAC8;'>
                                    <h1>Resultados </h1>
                                        <ul>
                            """
        for item in lista:
            lista_html += "<li>" + item + "</li>"

        lista_html += """
                                        </ul>
                                    </body>
                                </html>
                            """
        return lista_html

    def do_GET(self):
        lista_recursos = self.path.split("?")
        if len(lista_recursos) > 1:
            parametros = lista_recursos[1]
        else:
            parametros = ""

        if parametros:
            limit_parametros = parametros.split("=")
            try:
                if limit_parametros[0] == "limit":
                    limit=int(limit_parametros[1])
                    if limit>100:
                        limit=1
            except ValueError:
                limit=1

        if self.path=='/':

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()  # crea el formulario ya que llama al metodo 'dame_pag_principal'.
            html=self.formulario()
            self.wfile.write(bytes(html, "utf8"))

        elif 'listDrugs' in self.path: #Pedimos realizar una lista de medicamentos en pag web.
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            lista_drogas = []
            resultados_obtenidos = self.obtener_resultados(limit) #llamamos a la funcion para obtener los datos.
            for resultado in resultados_obtenidos:
                if ('generic_name' in resultado['openfda']):
                    lista_drogas.append (resultado['openfda']['generic_name'][0])
                else:
                    lista_drogas.append('Nombre del medicamento desconocido.')
            final_html = self.pagina_web(lista_drogas) #llamamos al metodo dame_pag_web para realizar la pagina web.

            self.wfile.write(bytes(final_html, "utf8"))
        elif 'listCompanies' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            lista_companies = []
            resultados_obtenidos = self.obtener_resultados (limit)
            for resultado in resultados_obtenidos:
                if ('manufacturer_name' in resultado['openfda']):
                    lista_companies.append (resultado['openfda']['manufacturer_name'][0])
                else:
                    lista_companies.append('El nombre de la empresa es desconocido')
            final_html = self.pagina_web(lista_companies)

            self.wfile.write(bytes(final_html, "utf8"))
        elif 'listWarnings' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            lista_warnings = []
            resultados_obtenidos = self.obtener_resultados (limit)
            for resultado in resultados_obtenidos:
                if ('warnings' in resultado):
                    lista_warnings.append (resultado['warnings'][0])
                else:
                    lista_warnings.append('La advertencia es desconocida.')
            final_html = self.pagina_web(lista_warnings)

            self.wfile.write(bytes(final_html, "utf8"))
            #se realizara para company y warnings el mismo proceso realizado para drugs.
        elif 'searchDrug' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            limit = 10
            drug=self.path.split('=')[1]

            list_drugs = []
            conexion = http.client.HTTPSConnection(self.OPENFDA_URL)
            conexion.request("GET", self.OPENFDA_EVENTO + "?limit="+str(limit) + self.OPENFDA_DROGA + drug)
            r1 = conexion.getresponse()
            info1 = r1.read()
            info_raw = info1.decode("utf8")
            informacion = json.loads(info_raw)

            try:
                buscador_drugs = informacion['results']
                for resultado in buscador_drugs:
                    if ('generic_name' in resultado['openfda']):
                        list_drugs.append(resultado['openfda']['generic_name'][0])

                    else:
                        list_drugs.append('Medicamento desconocido.')


            except KeyError:  #En caso de introducir una droga incorrecta o no introducir ninguna, lo trataremos mediante un except.
                list_drugs.append('Busqueda erronea, introduzca nombre correcto.')
            final_html = self.pagina_web(list_drugs)
            self.wfile.write(bytes(final_html, "utf8"))

        elif 'searchCompany' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            limit = 10
            company=self.path.split('=')[1]
            list_companies = []
            conexion = http.client.HTTPSConnection(self.OPENFDA_URL)
            conexion.request("GET", self.OPENFDA_EVENTO + "?limit=" + str(limit) + self.OPENFDA_COMPANIA + company)
            r1 = conexion.getresponse()
            info1 = r1.read()
            info_raw = info1.decode("utf8")
            informacion = json.loads(info_raw)
            try:
                buscador_company = informacion['results']

                for resultado in buscador_company:
                    if ('manufacturer_name' in resultado['openfda']):
                        list_companies.append(resultado['openfda']['manufacturer_name'][0])

                    else:
                        list_companies.append('Empresa desconocida.')

            except KeyError:
                list_companies.append('Busqueda erronea, introduzca un nombre correcto.')
            final_html = self.pagina_web(list_companies)
            self.wfile.write(bytes(final_html, "utf8"))
        elif 'redirect' in self.path: #Redireccion a la pagina principal.
            self.send_response(302)
            self.send_header('Location', 'http://localhost:'+str(Puerto))
            self.end_headers()
        elif 'secret' in self.path: #En caso de que sea una URL de acceso restringido, recibiremos un error 401.
            self.send_error(401)
            self.send_header('WWW-Authenticate', 'Basic realm="Mi servidor"')
            self.end_headers()
        else: # Si el recurso solicitado no se encuentra en el servidor, recibiremos un mensaje de error 404.
            self.send_error(404)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(". Recurso no encontrado: '{}'.".format(self.path).encode())
        return



socketserver.TCPServer.allow_reuse_address= True
# El servidor comienza aquí:

Handler = testHTTPRequestHandler #Establecemos como manejador nuestra propia clase, llamada Handler (objeto).

httpd = socketserver.TCPServer(("", Puerto), Handler)# Configuramos el socket del servidor, esperando conexiones
# de clientes.
print("Servidor en el puerto", Puerto)
# Entramos en el bucle principal, atendiendo las peticiones desde nuestro manejador (cada vez que ocurra un 'GET'
# se invocará nuestro método do_GET)
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("")
    print("Servidor interrumpido por el usuario.")
exit(1)# Salimos del código si el usuario interrumpe el server.
