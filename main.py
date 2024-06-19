import boto3
import datetime
import random
import time
 
# AWS SiteWise Alias
aliasBedroomConsumedEnergy = '/bedroom/energyConsumed'
aliasBedroomCurrentEnergy = '/bedroom/currentEnergy'
aliasBedroomOutsideTemp = '/bedroom/outsideTemp'
aliasBedroomRoomTemp = '/bedroom/roomTemp'
aliasBedroomTimeSpent = '/bedroom/timeSpent'

aliasAirConditionerIsTurnedOn = '/bedroom/airConditioner/isTurnedOn'
aliasHeaterFloorIsTurnedOn = '/bedroom/heaterFloor/isTurnedOn'
aliasClasicHeaterIsTurnedOn = '/bedroom/clasicHeater/isTurnedOn'

normalTemp = 20
outsideTemp = int(round(random.uniform(-30, 0), 2))
currentTemp = outsideTemp
hoursSpent = 0
totalEnergy = 0
 
# Create a Boto3 SiteWise client (Make sure region_name is the one you plan to use)
client = boto3.client('iotsitewise', region_name='eu-central-1')
tempDecresePerHour = client.get_asset_property_value(
    assetId='d58fd14b-0f55-411f-84cf-713f170fc67f',
    propertyId='607724f0-1f02-48ae-97d0-6fb10dc36402'
)['propertyValue']['value']['integerValue']

airCondMaxTempIncrease = client.get_asset_property_value(
    assetId='d7030558-9413-466f-8089-18e5aa8273f8',
    propertyId='f667abca-108d-42e6-a74b-4dc46472a6cb'
)['propertyValue']['value']['integerValue']
airCondPowerPerHour = client.get_asset_property_value(
    assetId='d7030558-9413-466f-8089-18e5aa8273f8',
    propertyId='8305d15c-023b-4062-8973-bf28d6629deb'
)['propertyValue']['value']['integerValue']
airCondTimeToMax = client.get_asset_property_value(
    assetId='d7030558-9413-466f-8089-18e5aa8273f8',
    propertyId='16382b51-fbb4-44f7-acde-63f25d2d4c54'
)['propertyValue']['value']['doubleValue']

heaterFloorMaxTempIncrease = client.get_asset_property_value(
    assetId='7c95af68-cdec-44c8-84d5-ac929d48a9e6',
    propertyId='f667abca-108d-42e6-a74b-4dc46472a6cb'
)['propertyValue']['value']['integerValue']
heaterFloorPowerPerHour = client.get_asset_property_value(
    assetId='7c95af68-cdec-44c8-84d5-ac929d48a9e6',
    propertyId='8305d15c-023b-4062-8973-bf28d6629deb'
)['propertyValue']['value']['integerValue']
heaterFloorTimeToMax = client.get_asset_property_value(
    assetId='7c95af68-cdec-44c8-84d5-ac929d48a9e6',
    propertyId='16382b51-fbb4-44f7-acde-63f25d2d4c54'
)['propertyValue']['value']['doubleValue']

clasicHeaterMaxTempIncrease = client.get_asset_property_value(
    assetId='22690fd9-ab0d-4491-a9dc-fb512f846372',
    propertyId='f667abca-108d-42e6-a74b-4dc46472a6cb'
)['propertyValue']['value']['integerValue']
clasicHeaterPowerPerHour = client.get_asset_property_value(
    assetId='22690fd9-ab0d-4491-a9dc-fb512f846372',
    propertyId='8305d15c-023b-4062-8973-bf28d6629deb'
)['propertyValue']['value']['integerValue']
clasicHeaterTimeToMax = client.get_asset_property_value(
    assetId='22690fd9-ab0d-4491-a9dc-fb512f846372',
    propertyId='16382b51-fbb4-44f7-acde-63f25d2d4c54'
)['propertyValue']['value']['doubleValue']
maxTempIncArray = [clasicHeaterMaxTempIncrease, heaterFloorMaxTempIncrease, airCondMaxTempIncrease]

while True:
    epoch = int(time.time())
    roomPayload = {
       "entries": [
            {
                "entryId": str(epoch) + 'total',
                "propertyAlias": aliasBedroomConsumedEnergy,
                "propertyValues": [
                    {
                        "value": {
                            "integerValue": totalEnergy
                        },
                        "timestamp": {
                            "timeInSeconds": epoch
                        },
                        "quality": "GOOD"
                    }
                ]
            },
            {
                "entryId": str(epoch) + 'outside',
                "propertyAlias": aliasBedroomOutsideTemp,
                "propertyValues": [
                    {
                        "value": {
                            "integerValue": outsideTemp
                        },
                        "timestamp": {
                            "timeInSeconds": epoch
                        },
                        "quality": "GOOD"
                    }
                ]
            },
            {
                "entryId": str(epoch) + 'currentTemp',
                "propertyAlias": aliasBedroomRoomTemp,
                "propertyValues": [
                    {
                        "value": {
                            "integerValue": int(currentTemp)
                        },
                        "timestamp": {
                            "timeInSeconds": epoch
                        },
                        "quality": "GOOD"
                    }
                ]
            },
            {
                "entryId": str(epoch) + 'timespent',
                "propertyAlias": aliasBedroomTimeSpent,
                "propertyValues": [
                    {
                        "value": {
                            "doubleValue": hoursSpent
                        },
                        "timestamp": {
                            "timeInSeconds": epoch
                        },
                        "quality": "GOOD"
                    }
                ]
            }
        ] 
    }
    try:
        response = client.batch_put_asset_property_value(entries=roomPayload['entries'])
        print("Data sent successfully", 'ROOM DATA SEND', totalEnergy, outsideTemp,currentTemp, hoursSpent)
    except Exception as e:
        print("Error sending data: {}".format(e))
    
    tempDiff = normalTemp - currentTemp
    turnedOnCond = 0
    turnedOnFloor = 0
    turnedOnHeater = 0
    
    calcSumFlag = 1
    
    if tempDiff == airCondMaxTempIncrease:
        calcSumFlag = 0
        turnedOnCond = 1
        
    if tempDiff == heaterFloorMaxTempIncrease:
        calcSumFlag = 0
        turnedOnFloor = 1
        
    if tempDiff == clasicHeaterMaxTempIncrease:
        calcSumFlag = 0
        turnedOnHeater = 1
        
    if calcSumFlag == 1:
        i = 0
        currentTempDiff = tempDiff
        while currentTempDiff > 0:
            currentTempDiff = currentTempDiff - maxTempIncArray[i]
            i += 1
        
        if i == 1:
            turnedOnHeater = 1
        
        if i == 2:
            turnedOnHeater = 1
            turnedOnFloor = 1
        
        if i == 3:
            turnedOnHeater = 1
            turnedOnFloor = 1
            turnedOnCond = 1
            
    currentEnergy = 0
    condPayload = {
        "entries": [
            {
                "entryId": str(epoch) + 'cond',
                "propertyAlias": aliasAirConditionerIsTurnedOn,
                "propertyValues": [
                    {
                        "value": {
                            "booleanValue": bool(turnedOnCond)
                        },
                        "timestamp": {
                            "timeInSeconds": epoch
                        },
                        "quality": "GOOD"
                    }
                ]
            },
        ]
    }
    
    try:
        response = client.batch_put_asset_property_value(entries=condPayload['entries'])
        print("Data sent successfully", 'COND DATA SEND')
    except Exception as e:
        print("Error sending data: {}".format(e))
            
    if turnedOnCond == 1:
        currentEnergy += airCondPowerPerHour
        currentTemp += airCondMaxTempIncrease / airCondTimeToMax
    
    heaterPayload = {
        "entries": [
            {
                "entryId": str(epoch) + 'heater',
                "propertyAlias": aliasClasicHeaterIsTurnedOn,
                "propertyValues": [
                    {
                        "value": {
                            "booleanValue": bool(turnedOnHeater)
                        },
                        "timestamp": {
                            "timeInSeconds": epoch
                        },
                        "quality": "GOOD"
                    }
                ]
            },
        ]
    }
    
    try:
        response = client.batch_put_asset_property_value(entries=heaterPayload['entries'])
        print("Data sent successfully", 'HEATER DATA SEND')
    except Exception as e:
        print("Error sending data: {}".format(e))
            
    if turnedOnHeater == 1:
        currentEnergy += clasicHeaterPowerPerHour
        currentTemp += clasicHeaterMaxTempIncrease / clasicHeaterTimeToMax
    
    floorPayload = {
        "entries": [
            {
                "entryId": str(epoch) + 'floor',
                "propertyAlias": aliasHeaterFloorIsTurnedOn,
                "propertyValues": [
                    {
                        "value": {
                            "booleanValue": bool(turnedOnFloor)
                        },
                        "timestamp": {
                            "timeInSeconds": epoch
                        },
                        "quality": "GOOD"
                    }
                ]
            },
        ]
    }
    
    try:
        response = client.batch_put_asset_property_value(entries=floorPayload['entries'])
        print("Data sent successfully", 'FLOOR DATA SEND')
    except Exception as e:
        print("Error sending data: {}".format(e))
    
    if turnedOnFloor == 1:
        currentEnergy += heaterFloorPowerPerHour
        currentTemp += heaterFloorMaxTempIncrease / heaterFloorTimeToMax
    
    currentEnergyPayload = {
        "entries": [
            {
                "entryId": str(epoch) + 'currentEnergy',
                "propertyAlias": aliasBedroomCurrentEnergy,
                "propertyValues": [
                    {
                        "value": {
                            "integerValue": currentEnergy
                        },
                        "timestamp": {
                            "timeInSeconds": epoch
                        },
                        "quality": "GOOD"
                    }
                ]
            },
        ]
    }
        
    try:
        response = client.batch_put_asset_property_value(entries=currentEnergyPayload['entries'])
        print("Data sent successfully",'ROOM CURRENT ENERGY', currentEnergy)
    except Exception as e:
        print("Error sending data: {}".format(e))

    totalEnergy += currentEnergy
    currentTemp -= tempDecresePerHour
    hoursSpent += 1
    
    time.sleep(3)
