# AWS Lambda Python com AWS RDS #

Demonstrar como criar rápido uma função AWS lambda em Python que realiza interações com uma base de dados AWS RDS.

> As opções utilizadas consideram ambiente exclusivamente para experimentação.
> Ambientes corporativos produtivos devem levar em consideração outros aspectos não contemplados, como segurança, capacidade, alta disponibilidade e *observability*.

> Referências
  - [https://docs.aws.amazon.com/pt_br/lambda/latest/dg/services-rds-tutorial.html](https://docs.aws.amazon.com/pt_br/lambda/latest/dg/services-rds-tutorial.html)
  - [https://docs.aws.amazon.com/pt_br/lambda/latest/dg/getting-started-create-function.html](https://docs.aws.amazon.com/pt_br/lambda/latest/dg/getting-started-create-function.html)


## Passo 1

O primeiro passo é criar uma base de dados RDS.

1. Faça login no AWS Console.

2. Em **Serviços** selecione **RDS**.

3. Selecione o botão **Create database**.

4. Na tela de criação do banco preencha as informações abaixo e selecione o botão **Create database**.

   - Choose a database creation method: `Standard create`
   - Engine type: `MySQL`
   - Template: `Free Tier`
   - DB instance identifier: `{RDS_INSTANCE_NAME}`
   - Master password: `{RDS_MASTER_PASSWORD}`
   - Confirm password: `{RDS_MASTER_PASSWORD}`
   - Enable storage autoscaling: `desabilitado`
   - Virtual private cloud (VPC): `Default VPC`
   - Public access: `Yes`
   - Initial database name: `{DB_NAME}`
   - Enable automatic backups: `desabilitado`
   - Enable auto minor version upgrade: `desabilitado`

     > Escolha um conteúdo a sua escolha para as variáveis `{RDS_INSTANCE_NAME}`, `{RDS_MASTER_PASSWORD}` e `{DB_NAME}` e guarde pois serão utilizados posteriormente.

     > Caso não exista uma **Default VPC**, crie utilizando conforme [https://docs.aws.amazon.com/vpc/latest/userguide/default-vpc.html](https://docs.aws.amazon.com/vpc/latest/userguide/default-vpc.html).

     > Mantenha as demais opções padrões.

5. Selecione a instância RDS criada e capture o Endpoint que será utilizado posteriormente.

   > Posteriormente esse valor será mencionado como **{RDS_ENDPOINT}**.


## Passo 2

Libere o Security Group para permitir conexões TCP na porta 3306.

1. Em **Serviços** selecione **VPC**.

2. No menu esquerdo selecione **Security Groups**.

3. Selecione o Security Group `default`.

4. Em `Inbound rules` clique em `Edit inbound rules`.

5. Em `Source` selecione `0.0.0.0/0` e clique em `Save rules`.


## Passo 3

Realizar o acesso programático com sua conta AWS via AWS CLI.

> Referência [https://aws.amazon.com/pt/cli/](https://aws.amazon.com/pt/cli/)

> O *Access Key Id* e o *Secret Key* podem ser gerados em [https://console.aws.amazon.com/iam/home#security_credential](https://console.aws.amazon.com/iam/home#security_credential)

Abra o prompt de comando digite `aws configure` e informe os parâmetros solicitados da sua conta.


## Passo 4

Criar pacote de implantação.

O código da função AWS Lambda consiste em scripts ou programas compilados e as dependências deles.

> Para facilitar a execução sugerimos um terminal Linux.
> Opção: [MobaXterm](https://mobaxterm.mobatek.net/download-home-edition.html).

1. Abra um prompt de comando, crie o diretório `rds` e navegue até ele.

   ```
   mkdir rds
   cd rds
   ```

2. Copie o conteúdo dos arquivo Python [rds.py](https://github.com/kledsonhugo/aws-lambda-python-with-rds/blob/main/rds.py) e [rds_config.py](https://github.com/kledsonhugo/aws-lambda-python-with-rds/blob/main/rds_config.py) do GitHub e salve-o no diretório `rds`. A estrutura do seu diretório deve ficar assim:

   > Substitua o conteúdo do arquivo `rds_config.py` com as variáveis `{RDS_ENDPOINT}`, `{RDS_MASTER_PASSWORD}` e `{DB_NAME}` capturadas nos passos anteriores.

   ```
   ls
   | rds.py
   | rds_config.py
   ```

3. Instale e copie a biblioteca de dependência Python `PyMySQL`.

   > Verifique o conteúdo da variável {PATH_OF_PYTHON_LIBRARIES} e substitua no comando `cp`.

   ```
   python -m pip install PyMySQL
   cp -aR {PATH_OF_PYTHON_LIBRARIES} .
   ls
   | rds.py
   | rds_config.py
   | rds\   
   ```

4. Adicione o conteúdo do diretório `rds` no arquivo `rds.zip`.

   > Caso esteja utilizando o MobaXterm e o comando zip não esteja disponível, digite `apt-get install zip` para instalar.

   ```
   zip -r rds.zip pymysql/
   zip rds.zip rds.py
   zip rds.zip rds_config.py
   ```

   > Referência [https://docs.aws.amazon.com/pt_br/lambda/latest/dg/python-package-create.html](https://docs.aws.amazon.com/pt_br/lambda/latest/dg/python-package-create.html)


## Passo 5

Crie a função de execução que dá à sua função permissão para acessar recursos do AWS.

1. Abra a página [Roles](https://console.aws.amazon.com/iam/home#/roles) no console do IAM.

2. Selecione `Create role`.

3. Crie uma função com as seguintes propriedades.

   - Entidade confiável: `Lambda`
   - Permissões: `AWSLambdaVPCAccessExecutionRole`
   - Nome da função: `lambda-vpc-role`


## Passo 6

Crie a função AWS Lambda com o comando `create-function`.

> Você encontra o ID da conta em [My Account](https://console.aws.amazon.com/billing/home?#/account).
> Você encontra os ID´s das Subnets e o ID do Security Group da VPC padrão nas configurações da instância RDS.

```
aws lambda create-function --function-name  PythonWithRds --runtime python3.8 \
--zip-file fileb://rds.zip --handler rds.handler \
--role arn:aws:iam::{ACCOUNT_ID}:role/lambda-vpc-role \
--vpc-config SubnetIds={SUBNET_ID_1},{SUBNET_ID_2},{SUBNET_ID_N},SecurityGroupIds={SECURITY_GROUP_NAME}
```

Exemplo de output

```
aws lambda create-function --function-name  PythonWithRds --runtime python3.8 --zip-file fileb://rds.zip --handler rds.handler --role arn:aws:iam::940570436032:role/lambda-vpc-role --vpc-config SubnetIds=subnet-0a08743f7800e83a3,subnet-019236c91c5140946,subnet-0e7bfc0e8aa88d7e6,subnet-0e7ef421411dfb147,subnet-03c0ea1041870d016,subnet-09254ac236b1ef53c,SecurityGroupIds=sg-077bde7a1e4adffb6
{
    "FunctionName": "PythonWithRds",
    "FunctionArn": "arn:aws:lambda:us-east-1:940570436032:function:PythonWithRds",
    "Runtime": "python3.8",
    "Role": "arn:aws:iam::940570436032:role/lambda-vpc-role",
    "Handler": "rds.handler",
    "CodeSize": 100071,
    "Description": "",
    "Timeout": 3,
    "MemorySize": 128,
    "LastModified": "2021-04-07T22:52:07.186+0000",
    "CodeSha256": "ow8X72ElELRtE0Qwt8y+WBfG9JWI996WwUhD0cDoLyk=",
    "Version": "$LATEST",
    "VpcConfig": {
        "SubnetIds": [
            "subnet-03c0ea1041870d016",
            "subnet-0e7bfc0e8aa88d7e6",
            "subnet-0e7ef421411dfb147",
            "subnet-0a08743f7800e83a3",
            "subnet-09254ac236b1ef53c",
            "subnet-019236c91c5140946"
        ],
        "SecurityGroupIds": [
            "sg-077bde7a1e4adffb6"
        ],
        "VpcId": "vpc-01e6c131d49579083"
    },
    "TracingConfig": {
        "Mode": "PassThrough"
    },
    "RevisionId": "4c1b1178-2d5e-4598-a730-9a1569e0eae2",
    "State": "Pending",
    "StateReason": "The function is being created.",
    "StateReasonCode": "Creating",
    "PackageType": "Zip"
}
```


## Passo 7

Nesta etapa você invoca a função do Lambda manualmente usando o comando `invoke`.

Quando a função do Lambda é executada, ela executa a consulta SELECT para a tabela *Users* na instância MySQL do RDS e imprime os resultados, que também vão para o CloudWatch Logs.

1. Invoque a função do Lambda com o comando invoke.

   `rds $ aws lambda invoke --function-name PythonWithRds output.txt`

2. Verifique se a função Lambda foi executada com êxito, da seguinte forma:

   - Analise o arquivo output.txt.
   - Analisar os resultados no console do AWS Lambda.
   - Verifique os resultados no CloudWatch Logs.


## Passo 8

A menos que você queira manter os recursos criados neste tutorial, você poderá excluí-los agora.

Excluindo os recursos da AWS que você não está mais usando, você evita cobranças desnecessárias em sua conta da AWS.

1. Para excluir a função Lambda.

   - Abra a página [Funções](https://console.aws.amazon.com/lambda/home#/functions) do console do Lambda.
   - Selecione a função criada.
   - Escolha **Actions**, **Delete**.
   - Escolha **Delete**.

2. Para excluir a função de execução.

   - Abra a página [Funções](https://console.aws.amazon.com/iam/home#/roles) do console do IAM.
   - Selecione a função de execução criada.
   - Selecione **Delete role (Excluir função)**.
   - Escolha **Sim**, **excluir**.

3. Como excluir a instância de banco de dados MySQL.

   - Abra a página [Bancos de dados](https://console.aws.amazon.com/rds/home#databases:) do console do Amazon RDS.
   - Selecione o banco de dados criado.
   - Escolha **Actions**, **Delete**.
   - Desmarque a caixa de seleção **Create final snapshot (Criar snapshot final)**.
   - Digite `delete me` na caixa de texto.
   - Escolha **Delete (Excluir)**.
