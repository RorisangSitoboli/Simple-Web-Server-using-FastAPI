from typing import Optional
from fastapi import FastAPI, Body, Request
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import json

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/ping")
async def home():
        return {"msg": "pong"}
        

# Login details.
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
	print(form_data)
	with open("userdb.json", "r") as json_file:
		json_data = json.load(json_file)
	if json_data:
		# Check if username exists.
		password = json_data.get(form_data.username)
		if not password:
			print("Warning! Your username or password is incorrect. Please re-enter.")
			raise HTTPException(status_code=403, detail="Incorrect username or password.")
			 
	# Check if the username is in the DB, and that password is a positive match
	return {"access_token": form_data.username, "token_type": "bearer"}

@app.get("/spend/history")
def spend_history(token: str = Depends(oauth2_scheme)):
	print(token)
	# Spend history logic
	with open("spendhist.json", "r") as spend_hist:
		spend_hist_data = json.load(spend_hist)
		if not spend_hist_data.get(token):
			raise HTTPException(status_code=400, detail="Username not found in spend history DB ")
	return {
		"username": token,
		"spend_hist": spend_hist_data[token]
		}

@app.get("/creditcard/history")
def credit_history(token: str= Depends(oauth2_scheme)):
	print(token)                                                                                                            
	# Credit history logic                                                                                                   
	with open("credithist.json", "r") as credit_hist:                                                                                 
		credit_hist_data = json.load(credit_hist)                                                                                 
		if not credit_hist_data.get(token):                                                                                              
			raise HTTPException(status_code=400, detail="Username not found in 'credit history DB'")                
	return {                                                                                                                        
		"username": token,                                                                                                      
	"credit_hist": credit_hist_data[token]                                                                                    
		}

# Funds transfer.
@app.post("/transfer_funds")
def transfer_funds(token: str = Depends(oauth2_scheme), destination_user: str = Body(...), amount_to_transfer: float = Body(...)):
    print(token)
    print(destination_user)
    print(amount_to_transfer)
    with open ("userbalance.json", "r") as userbalance_file:
        userbalance_data = json.load(userbalance_file)
        # Current user balance.
        curr_user_bal = userbalance_data.get(token)["curr_balance"]
        print(f"Current user balance: {curr_user_bal}")
		# Destination user balance.
        dest_user = userbalance_data.get(destination_user)
        if not dest_user:
            raise HTTPException(status_code=400, detail="Destination or Recepient is not found in DB. Transaction not cannot be completed!")
        dest_user_balance = dest_user["curr_balance"]
        print(f"Destination User Balance = {dest_user_balance}")
        if curr_user_bal - amount_to_transfer < 0:
            raise HTTPException(status_code=400, detail="You do not have an overdraft facility. Please specify a lower amount.")
    userbalance_data[token]["curr_balance"] -= amount_to_transfer
    print(userbalance_data)
    userbalance_data[destination_user]["curr_balance"] += amount_to_transfer
    with open("userbalance.json", "w") as userbal_write:
        json.dump(userbalance_data ,userbal_write)
    return {
            "username": token,
            "recepient": destination_user,
            "message": f"An amount of {amount_to_transfer} has been successfully transferred."         
            }
            
# Getters.
@app.get("/userbalance")
def get_userbalance(token: str = Depends(oauth2_scheme)):
        with open("userbalance.json", "r") as userfile:
            userbalance = json.load(userfile)
        if not userbalance.get(token):
            raise HTTPException(status_code=400, detail="Username not present in the userbalance DB")
        return {
                "username": token,
                "current_balance": userbalance.get(token)["curr_balance"]                
        }
        



# Run the API with uvicorn
# Will run on http://127.0.0.1:8000
if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
    
#uvicorn app:app --reload
