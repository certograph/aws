Deploying ResponderAPI into an Elastic Container Service Cluster
================================================================

In order to deploy **ResponderAPI** using Elastic Container Service (ECS) you will need an ECS cluster,
a Security Group, a **ResponderAPI** IAM ECS Task Execution Role with an accompanying policy, a **ResponderAPI** task 
definition, and a **ResponderAPI** service definition. Let's discuss how all of those puzzle pieces fit together.

**ResponderAPI** runs as a service inside an ECS cluster. You can deploy it into an existing cluster or
create a brand new one.

> **NOTE:** Before you do anything, check if the AWS region (see the upper right corner of the 
AWS console in your browser) is set to one of the AWS regions that **ResponderAPI** is available in.

## Deploying ResponderAPI

In order to have the best **ResponderAPI** deployment experience, you will need to have an active **ResponserAPI** AWS
Marketplace subscription, with will give you access to the **ResponderAPI** AWS ECR repository.
Once you subscribe, you will need to prepare a few essential resources.

> **NOTE:** The following instructions are designed to get you up and running in the shortest time possible. Make your 
> own adjustments as necessary. 

### Create an Amazon IAM Task Role

ECS tasks need two IAM roles, an IAM Task Role, and an IAM Task *Execution* Role. The IAM Task Execution Role is 
automatically assigned to each new task at the point of creation. Your account likely already has one, it's called 
`ecsTaskExecutionRole`. If it does not exist in your IAM account, your will need to create it and assign 
[this policy](ecsTaskExecutionRolePolicy.json) to it.

The ECS Task Role *is* likely missing and you will need to create it:

1. Go to the AWS IAM console and create a new role. Name it `ResponderAPIECSTaskRole`.
2. Assign 
[this policy](ResponderAPIECSTaskRolePolicy.json) to the new role.

### Create an Amazon Elastic Container Service (ECS) Task

Regardless of your choice of a new or existing cluster, you will need to create a **ResponderAPI** **Task Definition**.
An ECS *task* is the basis of a *service* that runs inside of an ECS *cluster*. In order to define a **ResponderAPI**
task, you will need a **ResponderAPI** container.

1. Select the AWS Region where you want to create a new ECS cluster.
2. Switch to the **Amazon Elastic Container Service** console. (You can type `ECS` into the search box in the upper left
   corner of the AWS Console.)
3. Click on the **Task Definitions** link in the left column in the **Amazon Elastic Container Service** console. 
4. Click on **Create new task definition** button. Please note that while there is an option to create a new task definition with JSON, it is a good options once you have created your first ***ResponderAPI** task definition and want to quickly create a new one with maybe small modifications. If it is your first time creating a ResponderAPI task definition, please follow the steps below.
5. On the **Task definition configuration** page, type something like *responderapi_task* into the **Task definition family** field.
6. Expand the **Infrastructure requirements** section and select **Launch type** for the task. Match it to the choice made in the **Infrastructure** section of the cluster definition you created earlier.
7. In the **OS, Architecture, Network mode** select either **Linux/X86_64** or **Linux ARM64**. This is largely a matter
of preference as the **ResponderAPI** Docker images are available for both architectures. Make sure you use the Docker image that matches the host architecture.
8. Leave **Network mode** as is.
9. In the **Task size**, select **CPU** **.5 vCPU**
10. In the **Memory** select **1GB**

    > There is no need to add storage to your **ResponderAPI host**. If you are concerned about log storage, 
**ResponderAPI** logs are automatically sent to **AWS CloudFront** log groups for your cluster. There is nothing to
configure unless you want to.

11. In the **Task roles** section select *ResponderAPIECSTaskRole* from the **Task role** list.
12. In the **Task execution role** section select *ecsTaskExecutionRole*.
13. In the **Container - 1** section, paste *ResponderAPI* Docker image URI into the **Image URI** field. You can find it in the ResponderAPI ECR repository.
14. In the **Port mappings** section, set **Container port** to *8080*, **Protocol** to *TCP*, and **App protocol** to *HTTP*.
15. In the **Resource allocation limits** set **CPU** to *0.5*, **Memory hard limit** to *1*, and **Memory soft limit** to *1*.
16. In the **Log collection** section, pick *Amazon CloudWatch* and accept default values.
17. In the **Healthcheck** section set **Command** to `/sbin/healthcheck --url=http://localhost:8080/healthcheck` (it's one line, do not add quotes or brackets)
18. Click **Create**

> **Tip**: Task definitions can be reused across ECS clusters.

### Create an Amazon Elastic Container Service (ECS) Cluster

**ResponderAPI** *container* will be used to define a *task* used create a *service* inside an ECS *cluster*. You can 
reuse an existing cluster or create a new one. If you wish to create a new ECS cluster, follow these steps.

1. Select the AWS Region where you want to create a new ECS cluster.
2. Switch to the **Amazon Elastic Container Service** console. (You can type `ECS` into the search box in the upper left 
corner of the AWS Console.)
3. Click on the **Create cluster** page, give your cluster a name you'll remember 
and expand the **Infrastructure** section. Pick either **AWS Fargate (serverless)** or **Amazon EC2 instances**. These 
will be used to host **ResponderAPI** Docker containers. 

### Create a ResponderAPI ECS Cluster Service Security Group

How you limit (or not) access to **ResponderAPI** will depend on your particular needs, but if you are
setting it up for the first time and want to confirm you can reach it, create a simple **Security Group**
in the same VPC that the services. The Security Group should have the following rules:

#### Inbound

* **Rule 1**: **IP Version**: `-`, **Type**: `All traffic`, **Protocol**: `All`, **Port range**: `All`, 
**Source**: `sg-`*id of this security group*`/default`, **Description**: `ResponderAPI Service Inbound Rule`
* **Rule 2**: **IP Version**: `IPv4`, **Type**: `Custom TCP`, **Protocol**: `TCP`, **Port range**: `8080`,
  **Source**: *you own public IP address*`/32`, **Description**: `ResponderAPI Service Client Inbound Rule`

#### Outbound

* **Rule 1**: **Type**: `All traffic`, **Protocol**: `All`, **Port range**: `All`, **Destination**: `0.0.0.0/0`, 
**Description**: `ResponderAPI Service Outbound`

> NOTE: The Security Group Rules are for initial testing only. You will need adapt them to your own particular case and 
> follow your organisation's security guidelines.

### Create a ResponderAPI ECS Cluster Service

1. You can now go to **Task definitions** click on the newly created task and click on the **Deploy** button. Select 
**Create service** from the drop down list.
2. On the **Create** page, select en existing ECS cluster or click on **Create a new cluster**
3. In the **Compute configuration** section, click on **Launch type**
4. In the **Launch type** select `FARGATE`
5. In the **Platform version** select `LATEST`.
6. In the **Deployment configuration** select **Application type** to be `Service`.
7. Name the new service `responderapi-service`.
8. In the **Service type** select `Replica`
9. Set **Desired tasks** to `1`
10. In the **Networking** section pick the Security Group you created earlier.
11. Enable **Public IP**
12. Click **Create**

Service deployments take a couple of minutes. You can watch deployment in the AWS **Cloud Formation** console.

If all goes well, you see the following message in the ``


```
ready to serve requests
```

* use the right ResponderAPI image of the host architecture. Every release of ResponderAPI is avilable for the amd64 or amd64 architectures
* make sure you use a security group that allows access from the IP addresses where your API client will be making calls, to keep things simple, use xxxxx tp find out what your public IP is and allow inbound TCP traffic to port 8080 
The simplest way to deploy ResponderAPI is to run a CloudFormation template



Task Service IAM Role Policy

Give it an easy to recognise name like `ResponderAPITaskServicePolicy`



## Diagnostics

The first time you deploy a new ECS service there is a lot to wrap your hed around, but as you may have noticed the only
**ResponderAPI**-specific configuration steps are choosing the **ResponderAPI** Docker image that matches the 
architecture of the hosts (`amd64` or `arm64`) and adding the `ResponderAPIECSTaskRole` with the accompanying [ResponderAPIECSTaskRolePolicy](ResponderAPIECSTaskRolePolicy.json)  

Still, things can go wrong and you may not succeed the first time you try. Here are ways you can quickly diagnose what's
going on. Frustratingly, you may have to poke around different AWS consoles, but at least you will learn something useful. 
The fix for all of those issues is to go through the steps described earlier and spot the places where you made mistakes.

If this is not the first time you are using ECS, you will knw what you do not have to start from scratch, but can just as
well create a new **ResponderAPI ECS Task Definition** revision and then update the **ResponderAPI** service that depends 
on it.

### Deployment Fails Altogether

Here are possible causes:

* **A mismatch of architectures**. This is an easy one to make. You are trying to run an AMD64 container on a ARM64 host or vice versa. You likely chose an `amd64` host, but put an `arm64` Docker image on it. You know that happened when you see the following line in the
`/ecs/responderapi-task` log group in **AWS CloudWatch**:

```
`exec /sbin/api-server: exec format error` 
```

* **Misconfigured Healthcheck**. Deployment starts fine, but it quickly fails. Have a look at the **AWS CloudFormation** 
console and look at stack events. If there is mention of the following events, you have likely not set up healthcheck 
correctly. Please make sure that you copy and paste the `healthcheck` command as described earlier in this document. 
The guidance given by AWS is slightly misleading, the syntax shown in the healthcheck field shows what that command will
be translated into when you deploy **ResponderAPI**. You can verify this if you look at the JSON definition of the **ResponderAPI** task.

```
CREATE_FAILED   The following resource(s) failed to create: [ECSService].

CREATE_FAILED   Resource handler returned message: "Error occurred during operation 'ECS Deployment Circuit Breaker was triggered'." (RequestToken: fa5467d3-dcd4-f587-01fb-9743b1e75e31, HandlerErrorCode: GeneralServiceException)
```

### ResponderAPI Deploys but Fails to Start and Exits Earl

* **Inactive Subscription to ResponderAPI**. If you try to run **ResponderAPI** without an active AWS Marketplace
subscription, you will see the error shown below. Go to the AWS Marketplace and
  search for `ResponderAPI` and subscribe.

    ```
    Unable to load SDK config
	
    Unable to obtain AWS credentials to make a call to the AWS API to confirm your entitlement (a check for an active
    subscription to ResponderAPI)
    ```

* **Missing ResponderAPIECSTaskRole**. If the CloudFormation deployment of the **ResponderAPI**

    ```
    Unable to register usage.
    ```

    This is fixed by creating a new task with the same settings and TaskRole of`

### Unknown Health Status of a Running ResponderAPI Task

If the health status of one or more of the **ResponderAPI** ECS tasks is reported as `Unknown` but the **ResponderAPI** 
service is alive and returns responses otherwise it means you have forgotten to define the healthcheck command for the
**ResponderAPI** ECS task. See instructions erlier in this document on how to fix it.

ResponderAPI may under some circumstances report other errors and exit. Since these are hard to predict, we are
not documenting them here, but we can give you some tips. If you see the task or pod crashing, it may be caused
by host instability or a lack of RAM. If you see persistent crashes, redeploy ResponderAPI using a host with more 
RAM. Redeploying Responder API should also take care of the unstable host issues.

1. You can now go to **Task definitions** click on the newly created task and click on the **Deploy** button. Select *Create service* from the drop down list.
2. On the **Create** page, select en existing ECS cluster or click on **Create a new cluster**
3. In the **Compute configuration** section, click on **Launch type**
4. In the **Launch type** select *FARGATE*
5. In the **Platform version** select *LATEST*.
6. In the **Deployment configuration** select **Application type** to be *Service*.
7. Name the new service **responderapi-service**.
8. In the **Service type** select *Replica*
9. Set **Desired tasks**to *1*
10. In the **Networking** section pick the Security Group you created earlier.
11. Enable **Public IP** 
12. Click **Create**

### Suport

Free support is available via the [issues page on GitHub](https://github.com/certograph/aws/issues). We
aim to answer your questions within 72 hours, Mon-Friday, London (UK) time.

Copyright (c) 2024, Certograph Ltd