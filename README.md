# IRK: IRC Bot 

## ABOUT                                                                                             
Just your average IRC bot written in python.    
Written by Grayson Miller.       
                            
## LICENSE                                      
Irk is licensed under the  GNU Affero General Public License v3.    
Refer to the LICENSE file before using Irk.   

## INSTALLING & RUNNING                                       
#### Requirements                                                                                      
* `nose`   
    
#### Testing from source root. (no install)   
`$ nosetests --nocapture`

#### Installing from CLI.                                       
`$ git clone git@github.com:GRAYgoose124/irk.git irk`  
`$ cd irk`                                           
`$ python setup.py install`                       

#### Running after installation.
`$ irk`   
(`CTRL+C` to safely quit or send the `!quit` command)
                                     
#### Uninstalling                                                                                           
`$ pip uninstall irk`                                

## PROJECT STATUS 
What version? Haha. Try 0.1.
                                            
### TODO 
* Plugins System
  * Permissions
  * Commands

* Proper Debug Logging
  * More debug loggings
  * Consistent and Clean

* IRC Logging
  * Individual channels/Queries to a file in folders for servers
  * No Extraneous data (only user & message per line in file)

### BUGS
Lots.
