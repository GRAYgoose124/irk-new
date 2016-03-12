# IRK: IRC Bot 

## ABOUT                                                                                             
Just your average IRC bot written in python.    
Written by Grayson Miller.       
                            
## LICENSE                                      
Irk is licensed under the GNU Affero General Public License v3.
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
Version 0.2
 Well... considering I have ~500 SLOC and a little bit going...

This code is more of a rough draft for a much needed rework at the moment.

### TODO

#1 Write API/docs, comments.

* cwdopen remove?
* Plugins System
  * Permissions
  * Commands
  * Document API
  * Can they be threaded effectively? (hooks have to be threaded too) so need async api with client)

* Proper Debug Logging (Remove logging module? It kinda sucks)
  * More debug loggings
  * Consistent and Clean

* IRC Logging
  * Individual channels/Queries to a file in folders for servers
  * No Extraneous data (only user & message per line in file)

  Logging plan: stdout is constant raw stream with minor pretty printing. + faulting errors
                file is the stream of logging data + all minor data.

* Reorganize file functions
  * I can factor out a couple functions if I initialize all files as I need them, not AOT
  * I can factor out the init or load config by combining with the init in client

* Threads & Optimization?
  * Probably not needed if I intend to monitor one server like foonetic...

* Housecleaning
  * This README
  * Everything
  * Comments
  * Start from line one.
    * Pass one: clean up everything that organization can fix.
    * Pass two: Determine what needs to be refactored and comment.
    * ...

### BUGS
Lots.
