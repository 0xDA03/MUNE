def generateDAT(path, filename, stimuli, responses):
    """ Export stimulus-response data from simulation to MScanFit-compatible .DAT file 
            filename - name to save file as
            stimuli - x-axis stimulus (mA) data
            responses - y-axis resposne (mV) data
    """
    
    with open(f"DAT/{path}/{filename}.DAT", "w") as file:
        for stimulus, response in zip(stimuli, responses):      # zip() function pairs elements from both arrays into tuples
            file.write(f"{stimulus:<30} {response}\r\n")        # \r\n is the MScanFit-compatible (Windows) newline character