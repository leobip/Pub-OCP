# SUMMARY

## Script to scan the Bitbucket Server to get all projects, repositories, branches & qry for the pullrequests (MERGED), pending test with github

- To Generate the user & password encripted: echo -n user:password | base64
- To promt user & pass
  - read -p "Enter your Bitbucket username: " u
  - response=$(curl -k -u $u -X GET -H "Content-type:.....

- Listos los CURL compuestos, usando variables, en el caso del Released, el AUTH se pasa por el docker RUN
- El script genera varios archivos al ejecutar, estan comentadas las llamadas:
  - scan-log.txt : Log de ejecución que va escribiendo el projecto que está consultando, repositorio, rama, para poder verificar en caso de fallo
  - prjs_list.txt : Lista de todos los projectos (Se puede habilitar)
  - repo_list.txt : Lista con projectos y sus repositorios (Se puede habilitar)
  - bitbucket-scan-results.csv : Lista de projectos, repositorios y sus ramas mergeadas, con fechas, destino, etc.

- He realizado varias pruebas y la consulta a la api de todas las ramas no es practica, se me ha ocurrido y he medio estructurado la funcion: get_branch_details para consultar de una en una las ramas y obrener la info, no está Lista.

- PROBLEMA: Tambien tenemos problema al ejecutar consulta sobre repos con nombres con nombres con espacios, al tomarlo para ejecutar la consulta toma solo el primer nombre....  - SOLUCIONADO: Con un replace, linea: 46

### Pending

- Consultar todas la ramas de un repo en un solo Curl y parsearlo para obtener los resultados de cada rama, para disminuir el tiempo de ejecución
  - Opción: Parsear la respuesta con un ciclo for y contador
