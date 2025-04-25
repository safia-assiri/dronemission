# dronemission
Drone &amp; Grow


a simple code that allows the drone to scan a specific area and perform a custom action to release seeds.
Before executing this action, the drone captures an aerial image of the area to document the pre-seeding state for later monitoring.
We tested the concept through simulation.

Tools:
1. px4 autopilot 
2. python


Code Steps:
1. connect to drone
2. ask the user to send the hight and width
3. arm the drone
4. aotomation takeoff
5. get the home position
6. start to scan as zigzag patrent to the hight and width specfiy
7. check battery for every movment to insure it can complete the task
