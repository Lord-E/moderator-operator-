# import time
import random_word 
r = RandomWords()

# Return a single random word
r.get_random_word()

print(r)
# print ("Start guessing...")
# time.sleep(0.5)

# #here we set the secret
# word = "secret"

# #creates an variable with an empty value
# guesses = ''

# #determine the number of turns
# turns = 10

# # Create a while loop

# #check if the turns are more than zero
# while turns > 0:         
# 	failed = 0             
   
# 	for char in word:      

# 		if char in guesses:    
	
# 			print (char,)    

# 		else:
	
# 		# if not found, print a dash
# 			print ("_",)     
	   
# 		# and increase the failed counter with one
# 			failed += 1    

# 	# if failed is equal to zero

# 	# print You Won
# 	if failed == 0:        
# 		print ("You won" ) 

# 	# exit the script
# 		break              



# 	# ask the user go guess a character
# 	guess = input("guess a character:") 

# 	# set the players guess to guesses
# 	guesses += guess                    

# 	# if the guess is not found in the secret word
# 	if guess not in word:  
 
# 	 # turns counter decreases with 1 (now 9)
# 		turns -= 1        
 
# 	# print wrong
# 		print ("Wrong")
  
 
# 	# how many turns are left
# 		print ("You have", + turns, 'more guesses' )
 
# 	# if the turns are equal to zero
# 		if turns == 0:           
	
# 		# print "You Lose"
# 			print( "You Lose")