
# Instrucciones para despliegue

### Paso 1: Clonar Repositorio

```zsh 
git clone https://github.com/ensamblador/serverles-reporting-api.git
```

Crear y activar un ambiente python virtual
(requiere virtualenv instalado)
```
cd serverles-reporting-api
virtualenv -p python3 .env
source .env/bin/activate
```
Instalar los modulos de python necesarios

```
pip install -r requirements.txt
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```
ver listado de aplicaciones

```
cdk ls
```

*Nota: si no ha ejecutado CDK debará generar un boostrap con el comando `cdk bootstrap`*

desplegar la aplicacion

```
cdk deploy
```

use `cdk deploy --profile <profile-name>` en caso de que quiera desplegar con credenciales distintas al profile por defecto.

eliminar la aplicacion

```
cdk destroy
```



## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
