# Bode-Plot

Create a bode plot with SDS10004X-E oscilloscope and DG1062Z function generator. 

# Background and Overview:

I had bought the SDS1004X-E oscilloscope because it seemed like a decent intro level digital oscilloscope (this is my first digital) and it advertised a Bode Plot function. I was especially interested in this bode plot function because I personally enjoyed building and testing filters when I was in school, and I wanted to dabble in some audio electronics and figured it would be a good tool to have. But I jumped the gun too quick and didn’t realize the bode plot function will only work with Siglent branded AWG, which, just my luck, I didn’t have. I did have a Rigol DG1062Z function generator though, and I set out on Google to see if I could get the Rigol one working.

And fortune was on my side, because someone had already figured out how to get the SDS1000X series of oscilloscopes to work with non-Siglent generators. Please check out Github user 4x1md and their project sds1004x_bode for a more elegant solution to this problem.

I am inexperienced with Python and don’t have a Linux machine though, and I couldn’t figure out how to write a driver for particular function generator. I tried to do it on a raspberry pi, but still no cigar. So instead, I decided to ignore the internal bode plot software of the SDS1004X-E and brute force program the instruments using Python. Here is that solution

Please remember, I am new to programming and this is basically the only experience I have writing I Python. I learned all I know of Python while doing this project. I know the way I am approaching this problem is rudimentary at best and it still has a lot of problems, but it works decently enough in its current state that I felt comfortable enough posting it here. I haven’t looked very hard for another solution that is similar to this one, but I am sure other people have done something similar to this before, and most likely better. I hope that someone out there who’s looking to make some basic bode plots can use this code, or someone can give me tips on improving on what I have so far. 

Thank you for reading!

# How to use the program:

I have only tested and executed this code in windows. I don’t know if or how it will perform on a Mac or Linux machine, since I only use a Windows machine at the moment. I am also using Python version 3.6.

I used the inquirer module as the basis of the user interface. As I understand it, the inquirer module only works when the code is run in the command prompt. So set your directory and run the code with the command “py BodePlotV2.py” or however you can run python code in the command prompt.

The code will ask you to select the VISA address of the instruments you are using. This is a good place to mention that this code also relies heavily on the pyvisa library to communicate with the instruments. Google it and follow the instructions for installation. I mostly tested this code using the USB interface because pyvisa will recognize USB connected measurement and test equipment with the Resource Manager. Use the arrow keys and ENTER to select the VISA resource that matches the prompt you’re given. If you’re connecting to your equipment over IP or you don’t see the resource listed, select the ‘Enter Manual’ option from the menu and enter the instrument visa address manually. Pyvisa module doesn’t recognize IP connected devices, so you will have to enter the address manually every time you run the code. I haven’t tested any GPIB connected devices either

After connection to the test equipment is established., the program will ask the user to input the signal generator amplitude, start frequency, stop frequency, and number of data points you wish to be taken. There is no input validation yet, so to keep the program from crashing, the data types must be int/float, int, int, int (respectively). The frequencies are in Hz as well. So, if you want to input 20kHz, only type in 20000. Input validation is something I’m currently working on for all points in the program.

At this point, channel 1 and 2 of both the oscilloscope and the generator will be on, and the function generator’s channel 1 and 2 will be outputting the same function. Now, adjust the vertical and horizontal scales of channel 1 and 2 of the oscilloscope to clearly see both waveforms. Press ENTER to start the sweep.

After the sweep completes successfully, the program will let you save the data collected during the sweep to an excel file, and it will provide a bode plot (magnitude and phase vs frequency response) for you to save manually. After completion, you’re given the option of running another scan or stopping the program.

I hope that whoever decides to use this code will find some use out of it, and will be able to improve upon it. Feel free to email me with any questions, and I will do my best to answer.

Thank you!
