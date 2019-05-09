import http.server
import http.client
import json
import socketserver

PORT = 8000
index_file_html = "index.html"
rest_servidor = "api.fda.gov"
label = "/drug/label.json"    #nombre del servidor REST

socketserver.TCPServer.allow_reuse_address = True

headers = {'User-Agent': 'http-client'}

class TestHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    # El metodo do_Get es el que se ejecuta automaticamente cuando alguien se conecte a mi servidor y pida un recurso.

    DROGA = '&search=active_ingredient:'
    COMPANY = '&search=openfda.manufacturer_name:'

    def index_html_2(self, lista):
        html_2 = (' <!DOCTYPE html>\n'
                        '<html lang="es">\n'
                        '<head>\n'
                        '<title>OpenFDA App</title>'
                        '</head>\n'
                        '<body style="background-color:  #ff3355;">\n'
                        '<h1> Usted ha pedido a siguiente información:: </h1>'
                        '\n'
                        '<ul>\n')

        for k in lista:
            html_2 += "<li>" + k + "</li>"

        html_2 += ('</ul>\n'
                    '\n'
                    '<a href="/">VOLVER A LA PAGINA PRINCIPAL</a>'
                    '</body>\n'
                    '</html>')

        return html_2

    #def pagina_principal(self):

        #with open("index.html", "r") as f:
            #index_file = f.read()

            #return index_file

    def pagina_principal(self):

        index_file = """
                <html>
                <head>
	                <meta charset="UTF-8">
    	                <title>Buscador de medicamentos</title>
                </head>
                <body align=center style='background-color:  #33ff71 '>
	                <h1>MENÚ</h1>
	                <br>
                     <form method="get" action="listDrugs">
                        <h3>MEDICAMENTOS</h3>
                        <p>Introduzca un limite:<p>
                        <input type = "submit" value="Buscar">
                        <input type = "text" name="limit"></input>
                        </input>
                    </form>
                    <br>
                    <form method="get" action="searchDrug">
	                <p>Introduzca un principio activo:<p>
                        <input type = "submit" value="Buscar">
                        <input type = "text" name="active_ingredient"></input>
                        </input>
                    </form>
                    <br>
                    <br>
                    <form method="get" action="listCompanies">
                    <h3>EMPRESAS</h3>
                    <p>Introduzca un limite:<p>
                        <input type = "submit" value="Buscar">
                    <input type = "text" name="limit"></input>
                        </input>
                    </form>
                    <br>
                    <form method="get" action="searchCompany">
                    <p>Introduzca un nombre:<p>
                        <input type = "submit" value="Buscar">
                        <input type = "text" name="company"></input>
                        </input>
                    </form>
                    <br>
                    <br>
                    <h3>ADVERTENCIAS</h3>
                    <p>Introduzca un limite<p>
                    <form method="get" action="listWarnings">
                        <input type = "submit" value="Buscar">
                    <input type = "text" name="limit"></input>
                        </input>
                    </form>
                    <br>
                    <br>
                    <p>ALUMNO: David Ferri Belenguer  EMAIL: d.ferri.2018@alumnos.urjc.es</p>
                </body>
                </html>
            """
        return index_file




    def conn_fda(self, limite=1, busqueda=""):
        #cadena de la petición

        dato_pedido = "{}?limit={}".format(label, limite)

        #si han pedido algo más en concreto lo añadimos a la cadena de peticion
        if busqueda != "":
            dato_pedido += "&{}".format(busqueda)

        print("URL: ",dato_pedido)

        #establecemos la conexion
        conexion = http.client.HTTPSConnection(rest_servidor)

        #enviamos la solicitud de la informacion desada
        conexion.request("GET", dato_pedido, None, headers)

        #respuesta del servidor
        r1 = conexion.getresponse()
        print("  * {} {}".format(r1.status, r1.reason))


        inf_json = r1.read().decode("utf8")

        conexion.close()

        return json.loads(inf_json)



    def list_medicamentos(self, limite, principio_activo=''):

        #nos devolerá la lista de medicamentos,con el límite que nosotros metamos
        if principio_activo:
            medicamentos = self.conn_fda(limite, self.DROGA + principio_activo)
            print('Principio activo correcto.')

        else:
            medicamentos = self.conn_fda(limite)
            print('No hemos encontrado el principio activo demandado.')
        # como es un diccionario, indexaremos los nombres de los medicamentos

        lista_medicamentos =[]

        for medicamento in medicamentos['results']:
            try:
                name = medicamento['openfda']['generic_name'][0]
            except KeyError:
                name = 'Desconocido'

            lista_medicamentos.append(name)

        #hacemos el HTML de la lista que se mostrará en pantalla
        return self.index_html_2(lista_medicamentos)



    def listado_empresas(self, limite,empresa=''):
        if empresa:
            medicamentos = self.conn_fda(limite, self.DROGA + empresa)
        else:
            medicamentos = self.conn_fda(limite)

        list_empresas = []

        for medicamento in medicamentos['results']:
            try:
                nombre_empresa = medicamento['openfda']['manufacturer_name'][0]
            except KeyError:
                nombre_empresa = 'Nombre desconocido'

            list_empresas.append(nombre_empresa)

        #hacemos el HTML de la lista creada de empresas que verá el cliente
        return self.index_html_2(list_empresas)



    def lista_adverts(self, limite):
        medicamentos = self.conn_fda(limite)

        list_adverts = []

        for medicamento in medicamentos['results']:
            try:
                advertencia = medicamento['warnings'][0]
            except KeyError:
                advertencia = 'Desconocida'

            list_adverts.append(advertencia)

        #hacemos el HTML con la lista creada de advertencias que verá el cliente
        return self.index_html_2(list_adverts)




    def html_erroneo(self):
        mensaje_html=(' <!DOCTYPE html>\n'
                        '<html lang="es">\n'
                        '<head>\n'
                        '<title>OpenFDA App</title>'
                        '</head>\n'
                        '<body style="background-color: #FB4343;">\n'
                        '<h1>Valores introducidos incorrectos, vuelva a intentarlo</h1>'
                        '\n'
                        '<ul>\n'
                        '<a href="/">VOLVER</a>'
                        '</body>\n'
                        '</html>')

        return mensaje_html


    def do_GET(self):
        print("Recurso pedido: {}".format(self.path))
        mensaje = ""

        # Partimos entre el endpoint y los parametros
        lista_pedido = self.path.split("?")
        endpoint = lista_pedido[0]

        #¿hay parametros?
        if len(lista_pedido) > 1:
            parametros = lista_pedido[1]
        else:
            parametros = ""

        limite = 1    # establecemos imite por defecto

        try:

            # Obtenemos los parametros
            if parametros:
                print("Se ha establecido un limite.")
                parametro_limite = parametros.split("=")


                if parametro_limite[0] == "limit":
                    limite = int(parametro_limite[1])    #expresamos el limite en un entero
                    print("Limit: {}".format(limite))
                elif parametro_limite[0] == 'active_ingredient':
                    principio_activo = str(parametro_limite[1])
                    print('PRINCIPIO ACTIVO:', principio_activo)

                elif parametro_limite == "company":
                    empresa = str(parametro_limite[1])
                    print('Empresa buscada:', empresa)

            else:
                limite = 1
                print("No se han introducido parmetros de búsqueda.")


            #dependiendo del botón pulsado, endpoint variará, y también lo hara la función a usar
            #e introducimos el límite obtenido

            if endpoint == "/":
                mensaje = self.pagina_principal()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(bytes(mensaje, "utf8"))


            elif endpoint == '/listWarnings' :
                print('Listado de posibles advertencias.')
                mensaje = self.lista_adverts(limite)
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(bytes(mensaje, "utf8"))

            elif endpoint=='/listDrugs':
                print('Lista de medicamentos en stock.')
                mensaje = self.list_medicamentos(limite)
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(bytes(mensaje, "utf8"))

            elif endpoint == '/searchDrug':
                print('Listado de medicamentos con el principio activo demandado.')
                limite =10
                mensaje = self.list_medicamentos(limite,parametros)
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(bytes(mensaje, "utf8"))

            elif endpoint=='/searchCompany':
                print('Lista de empresas existentes y disponibles.')
                limite=10
                mensaje = self.listado_empresas(limite,parametros)
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(bytes(mensaje, "utf8"))

            elif endpoint=='/secret':
                self.send_response(401)
                self.send_header('WWW-Authenticate', 'Basic realm="Mi servidor"')  # Le envias esa cabecera.
                self.end_headers()


            elif endpoint == '/listCompanies':
                print('Listado de empresas disponibles.')
                mensaje = self.listado_empresas(limite)
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(bytes(mensaje, "utf8"))


            elif endpoint=='/redirect':
                self.send_response(301)
                self.send_header('Location', 'http://localhost:' + str(PORT))
                self.end_headers()


            else:
                m_error = self.html_erroneo()
                self.send_response(404)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.end_headers()
                #self.wfile.write("No encuentro ese recurso '{}'.".format(self.path).encode())

                # En las siguientes lineas de la respuesta colocamos las
                # cabeceras necesarias para que el cliente entienda el
                # contenido que le enviamos (que sera HTML)
                #self.send_header('Content-type', 'text/html')
                #self.end_headers()

                # Enviar el mensaaje completo
                self.wfile.write(bytes(m_error, "utf8"))

        except KeyError:
            print('Lo siento, ese nombre no ha sido encontrado!')
            mensaje=self.html_erroneo()
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes(mensaje, "utf8"))

        except ValueError:
            print('Límite erróneo! Por favor, introduzca un nuevo limite.')
            mensaje=self.html_erroneo()
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes(mensaje, "utf8"))


        return



# Handler = http.server.SimpleHTTPRequestHandler
Handler = TestHTTPRequestHandler
# es una instancia de una clase que se encarga de responder a las peticciones http que puede venir un ordenador cualquiera o el test de la practica

httpd = socketserver.TCPServer(("", PORT), Handler)
print("Sirviendo en el puerto:", PORT)


try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("Puerto interrumpido por el usuario. Puerto:", PORT)
