# Python app building

This repository contains a `docker-compose` which starts up postgres, keydb (Redis),
rabbitmq and an example producer app which populates these services with some data.

Your task is to create a separate repo and write an application in Python,
which interacts with these services.

## Running this application stack

Install `docker-compose` and run with `docker-compose up --build`

## External services description

Credentials for postgres and rabbitmq: `user:password`. Keydb is configured with
protected mode disabled, so no credentials needed there.

1. In postgres there are following tables:

```
historical_transactions

id pk, provider_id fk, transaction_value
1, 1, 100
2, 1, 200
3, 2, -200

initial_data

id pk, provider_name, initial_value
1, Visa, 1000
2, Mastercard, 2000
```

2. Keydb is initially empty, but is expected to have values in the following format:

```
key, value
1_Visa, 1300
2_Mastercard, 1800
```

3. In rabbitmq there is a queue `incoming_transactions`, where incoming txs are sent to. Message format is as follows:

```
{
"id": 1,
"value": 600
}
```

## App logic

Subscribe to rmq queue `incoming_transactions`, read message data, write it to postgres table `historical_transactions`. Each 60s (at 00:00:00, 00:01:00 etc) update current value for each provider in keydb.

After processing example message, keydb data should look like this:

```
key, value
1_Visa, 1900
2_Mastercard, 1800
```

And `historical_transactions` in postgres:

```
id pk, provider_id fk, transaction_value
1, 1, 100
2, 1, 200
3, 2, -200
4, 1, 600
```

## Constraints and conditions

- Only one instance of application is ruining at the same time
- No other applications are using specified external services
- Values in Postgres and RMQ are correct and don't contradict each other (e.g. id not present in postgres won't appear in RMQ messages)
- Tolerance for update time of KeyDB data is ±1 second against system clock.

## Comments from candidate:

Hi! At first - thank you for giving me an opportunity - I really appreciate it. The task was interesting and engaging, but I’d like to share some thoughts and challenges I encountered.

There were a few aspects of the requirements that weren’t entirely clear to me. Unfortunately, due to some unexpected obligations earlier in the week, I could only dedicate significant time to the task starting Friday afternoon. As a result, I didn’t have an opportunity to ask clarifying questions before the weekend.

Despite this, I wanted to ensure I delivered a complete solution and even went a step further by exploring multiple approaches to the problem.

To address the ambiguity, I prepared three different solutions, each exploring a slightly different angle of the problem. You can find them in the following branches:

- f/first-solution-crontab
- f/second-solution-fifth-microsevice
- f/third-solution-multithreading

Below, I’ve provided a brief overview and analysis of each solution.

#### Important note
Before running the application using `docker compose`/`docker-compose`, please copy the environment variables template to a `.env` file:

```bash
cp .env.template .env
```

### First (branch name: f/first-solution-crontab)

This was the first approach that came to mind. However, upon reflection, I believe it might be the most complex solution due to its reliance on additional Linux packages. I wasn’t entirely sure whether using cron complied with the constraint: *No other applications are using specified external services* .

**Pros**

- The use of crontab reduces the number of tasks handled by the receiver.
- Crontab automatically triggers the script at the specified time, ensuring precise scheduling.
- It operates independently of the Python application.

**Cons**

- The execution time slightly exceeds the stated tolerance (*±1 second against the system clock*). I wasn’t sure if the requirement referred to the time data must be stored in KeyDB or the maximum processing time for saving data.
- Errors cannot be logged directly in the container logs.

### Second (branch name: f/second-solution-fifth-microsevice)

This solution feels the most appropriate for a microservice architecture. While it reduces the load on the receiver, I’m not entirely confident that it complies with all constraints (e.g., *Only one instance of the application is running at the same time*).

**Pros**

- Reduces the number of tasks assigned to the receiver.
- Accelerates the process of writing data to KeyDB (achieving sub-second timing).
- Aligns with the *Single Responsibility Principle (SRP)*.
- Offers better scalability and improved code organization.
- Easier to test compared to the first solution.

**Cons**

- Potential non-compliance with the “single instance” constraint.
- The `receiver` still doesn’t fully comply with *SRP*, even with the added microservice.

### Third (branch name: f/third-solution-multithreading)

This was the last solution I implemented, and I believe it best satisfies the constraints provided in the task.

**Pros**

- Leverages Python’s threading module, which is straightforward to use.
- Ensures compliance with all stated constraints.

**Cons**

- While threading is useful, Python’s *GIL* makes it less than ideal for certain workloads.
- Debugging this solution is more challenging.
- The order of thread execution can be unpredictable.
- Results in a more monolithic architecture, which might not scale as well as a microservice approach.

Once again, thank you for the opportunity to work on this task. I enjoyed the challenge and can see areas for further improvements in each of the solutions. I would greatly appreciate your feedback, especially regarding the use of threading in Python for this type of task.
