import boto3

s3_client = boto3.client("s3")

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('BikeRacks')

def lambda_handler(event, context):
    
    #transform crime data
    crime_file = s3_client.get_object(Bucket="bcitprojectdata", Key="crimedata_csv_all_years.csv")
    data = crime_file['Body'].read().decode('utf-8')
    crimes = data.split('\r\n')
    address_count = {}
    for crime in crimes:
        crime_data = crime.split(',')
        if(crime_data[0] == 'Theft of Bicycle'):
            if(crime_data[6] not in address_count):
                address_count[crime_data[6]] = 1
            else:
                address_count[crime_data[6]] = address_count[crime_data[6]] + 1
            
        
    #import rack data .csv to DynamoDB
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    s3_file_name = event['Records'][0]['s3']['object']['key']
    resp = s3_client.get_object(Bucket=bucket_name, Key=s3_file_name)
    data = resp['Body'].read().decode("utf-8")
    bike_racks = data.split('\r\n')
    id = 1
    for bike_rack in bike_racks:
        compare_num = ""
        thefts = 0
        rack_data = bike_rack.split(";")
        try:
            if(rack_data != "TYPE,YEAR,MONTH,DAY,HOUR,MINUTE,HUNDRED_BLOCK,NEIGHBOURHOOD,X,Y"):
                streetNumber = rack_data[0]
                streetName = rack_data[1]
                num_list = list(streetNumber)
                if(len(num_list) is 1):
                    num_list[0] = 'X'
                elif(len(num_list) is 2):
                    num_list[-1] = 'X'
                else:
                    num_list[-1] = 'X'
                    num_list[-2] = 'X'
                compare_num = "".join(num_list)
        except:
            print("")
        compare_address = f"{compare_num} {streetName}".upper()
        if(compare_address in address_count):
            thefts = address_count[compare_address]
        if(rack_data[0] != "Street Number"):
            table.put_item(
                Item = {
                    "Id" : id,
                    "streetNumber": rack_data[0],
                    "streetName": rack_data[1],
                    "numberOfRacks": rack_data[5],
                    "yearInstalled": rack_data[6],
                    "numberOfThefts": thefts
                }
            )
            id = id + 1
