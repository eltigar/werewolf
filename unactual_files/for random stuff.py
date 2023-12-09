months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
n = int(input("Enter a month number (1-12): "))
print("The month abbreviation is", months[n - 1] + ".", end='')
print(f"The month abbreviation is {months[n - 1]}.")
print("The mo\nth abbreviation is", months[n - 1] + ".", sep='|||||')
