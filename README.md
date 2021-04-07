# AWS Lambda Python com #

Demonstrar como criar rápido uma função AWS lambda em Python que realiza interações com uma base de dados AWS RDS.

> As opções utilizadas consideram ambiente exclusivamente para experimentação.
> Ambientes corporativos produtivos devem levar em consideração outros aspectos não contemplados, como segurança, capacidade, alta disponibilidade e observability.

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
   - DB instance identifier: `{RDS_INSTANCE_NAME}`  rdsinstance
   - Master password: `{RDS_MASTER_PASSWORD}`  admin123
   - Confirm password: `{RDS_MASTER_PASSWORD}`
   - Enable storage autoscaling: `desabilitado`
   - Virtual private cloud (VPC): `Default VPC`
   - Public access: `Yes`
   - Initial database name: `{DB_NAME}` usuarios
   - Enable automatic backups: `desabilitado`
   - Enable auto minor version upgrade: `desabilitado`

     > Escolha um conteúdo a sua escolha para as variáveis `{RDS_INSTANCE_NAME}`, `{RDS_MASTER_PASSWORD}` e `{DB_NAME}` e guarde pois serão utilizados posteriormente.

     > Caso não exista uma **Default VPC**, crie utilizando conforme [https://docs.aws.amazon.com/vpc/latest/userguide/default-vpc.html](https://docs.aws.amazon.com/vpc/latest/userguide/default-vpc.html).

     > Mantenha as demais opções padrões. 


## Passo 2

Criar pacote de implantação.

O código da função do AWS Lambda consiste em scripts ou programas compilados e as dependências deles. Use um pacote de implantação para implantar seu código de função no Lambda.

Criar o arquivo .zip que o Lambda usará como seu pacote de implantação.

> Para facilitar a execução sugerimos um terminal Linux.
> Opção: [MobaXterm](https://mobaxterm.mobatek.net/download-home-edition.html).

1. Abra um prompt de comando e crie um diretório de projeto do **`rds`**.

   `mkdir rds`

2. Navegue até o diretório de projeto do **`rds`**.

   `cd rds`

3. Copie o conteúdo do arquivo Python [rds.py](https://github.com/kledsonhugo/aws-lambda-python-with-rds/blob/main/rds.py) do GitHub e salve-o em um novo arquivo chamado **`rds.py`**. A estrutura do seu diretório deve ficar assim:

   ```
   rds $ ls
   | rds.py
   ```

4. Copie o conteúdo do arquivo Python [rds_config.py](https://github.com/kledsonhugo/aws-lambda-python-with-rds/blob/main/rds_config.py) do GitHub e salve-o em um novo arquivo chamado **`rds_config.py`**. A estrutura do seu diretório deve ficar assim:

   > Substitua o conteúdo do arquivo **`rds_config.py`** com as variáveis `{RDS_INSTANCE_NAME}`, `{RDS_MASTER_PASSWORD}` e `{DB_NAME}` capturadas nos passos anteriores.

   ```
   rds $ ls
   | rds.py
   | rds_config.py
   ```

5. Adicione os arquivos `rds.py` e `rds_config.py` à raiz do arquivo .zip.

   ```
   zip rds.zip rds.py
   zip rds.zip rds_config.py
   ```

     > Caso esteja utilizando o MobaXterm e o comando zip não esteja disponível, digite `apt-get install zip`.

## Passo 3

O terceiro passo é configurar o repositório GitHub e configurá-lo para sincronizar com o bucket S3.

1. Acesse o GitHub [https://github.com/](https://github.com/).

2. Selcione ou crie um repositório GitHub e acesse o menu **Settings**.

   > Referência [https://docs.github.com/pt/github/getting-started-with-github/create-a-repo](https://docs.github.com/pt/github/getting-started-with-github/create-a-repo).

3. Em **Secrets** clique em **New repository secret** e adicione as variáveis abaixo.

   - **`AWS_ACCESS_KEY_ID`** : `{AWS_ACCESS_KEY_ID}`
   - **`AWS_SECRET_ACCESS_KEY`** : `{AWS_SECRET_ACCESS_KEY}`

4. Publique arquivos no repositório GitHub que serão sincronizados com o bucket S3.

   > Caso tenha dúvidas para publicar conteúdo em repositório GitHub, consulte a doc oficial em [https://docs.github.com/pt/github/managing-files-in-a-repository/adding-a-file-to-a-repository-using-the-command-line](https://docs.github.com/pt/github/managing-files-in-a-repository/adding-a-file-to-a-repository-using-the-command-line).

5. Publique no repositório GitHub o arquivo `.github/workflows/main.yml` com o conteúdo abaixo.

   > Esse arquivo configura o Workflow de sincronismo do repositório GitHub com o bucket S3.

   > Substitua as variáveis `{REGIÃO_AWS}` e `{NOME_DO_BUCKET}` pelos valores capturados nos passos anteriores.

   ```
   name: Sync GitHub to S3

   on:
     push:
       branches:
       - master

   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:

       - name: Checkout repo
         uses: actions/checkout@v1

       - name: Set Credentials
         uses: aws-actions/configure-aws-credentials@v1
         with:
           aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
           aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
           aws-region: {REGIÃO_AWS}

       - name: Deploy objects to S3 bucket
         run: |
           aws s3 sync ./ s3://{NOME_DO_BUCKET} \
           --exclude '.git/*' \
           --exclude '.github/*' \
           --exclude 'README.md' \
           --acl public-read \
           --follow-symlinks \
           --delete
   ```

7. No repositório GitHub acesse a opção **Actions** e verifique o status da execução do Workflow.

   > Nesse ponto é esperado que o Workflow execute com sucesso e sincronize os arquivos do repositório GitHub com o Bucket S3.

   ![Workflow Actions](/images/workflow-actions.PNG)   

## Passo 4

Verifique no Bucket S3 se os objetos foram atualizados.

1. Faça login no AWS Console.

2. Em **Serviços** selecione **S3**.

3. Verifique a data e hora dos objetos no bucket.
