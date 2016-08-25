#whatwherewhen - lambda
A sample AWS Lambda function to parse emails

##Draft flow
 * SES address configured to listen for emails at whatwherewhen@DOMAINNAME.com
 * SES configured to write raw emails to S3 bucket
 * Lambda function listening for new emails in S3 bucket
 * Lambda function executes after receiving new mail
   * Searches email for all attached and embedded jpegs
   * Verifies EXIF GPS data present
   * If present, captures data in a tuple and strips all EXIF from the image
   * generates a thumbnail
   * uploads new image and thumbnail to S3

##Create lambda package
create a virtual environmnt in python and install the deps

`virtualenv venv`
`. ./venv/bin/activate`

`pip install -r requirements.txt`

create a zip file:
`cd venv/lib64/python2.7/site-packages/`

`zip -r9 /tmp/lambda_function.zip *`

Add your handler python file

`zip -g9 /tmp/lambda_function.zip YOURPYTHONFILE`


##TODO
Literally everything
