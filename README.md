Tech Stack- python, Django, SQL

API
1. upload/ -
       a. takes csv as input
       b. check the format
       c. call a async thread to execute operations to compress the image present in the input urls
       d. save the results into the DB.

2. status/request_id -
       a. takes request_id as parameter, filter all the request associated with it.
       b. return status and complete response with input and output urls.

for more clarification, check results.pdf in media/results.
       
