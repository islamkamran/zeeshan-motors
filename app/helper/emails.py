import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_otp_to_email(receiver_email: str, otp: str):
    sender_email = "info@bigstaruae.com"
    sender_password = "j9PYrxJ3eCZt"
    
    # Create a MIME message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Your OTP for Password Reset"
    
    # Create the email body
    body = f"Your One-Time Password (OTP) for password reset is: {otp}"
    message.attach(MIMEText(body, "plain"))
    
    try:
        # Set up the SMTP server and send the email
        with smtplib.SMTP("smtp.zoho.com", 587) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)  # Log in to your email
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("OTP email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")



def send_quote_to_email(veh_chassis:str, veh_name:str, veh_title:str, data):
    # Email sender configuration
    sender_email = "info@bigstaruae.com"
    sender_password = "j9PYrxJ3eCZt"
    # receiver_email = ["islamkamran332@gmail.com","m.islamkamran@gmail.com","mislamkamran@cs.qau.edu.pk"]
    receiver_email = ["info@bigstaruae.com ", "moazzamwalikhan@gmail.com", "m.umar@baiggrp.com"]

    # for i in range(len(receiver_email)):
        # Create a MIME message
    message = MIMEMultipart()
    message["From"] = sender_email
    # message["To"] = receiver_email
    message["To"] = ",".join(receiver_email)
    message["Subject"] = f"Quote for Vehicle with chassis: {veh_chassis}, Name: {veh_name} and Title: {veh_title}"
    # Create the email body
    body = f"User: {data.name},\nCountry: {data.country}, \nCity: {data.city}, \nPhone: {data.phone}, \nEmail: {data.email}, \nWhatsapp: {data.whatsapp} is asking for a quote for vehicle, \nwith remarks: {data.remarks}"
    message.attach(MIMEText(body, "plain"))
    try:
        # Set up the SMTP server and send the email
        with smtplib.SMTP("smtp.zoho.com", 587) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)  # Log in to your email
            # server.sendmail(sender_email, receiver_email, message.as_string())
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Quote email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")


def send_quote_to_email_truck(truck_chassis:str, truck_name:str, truck_title:str, data):
    # Email sender configuration
    sender_email = "info@bigstaruae.com"
    sender_password = "j9PYrxJ3eCZt"
    receiver_email = ["info@bigstaruae.com ", "moazzamwalikhan@gmail.com", "m.umar@baiggrp.com"]

    # for i in range(len(receiver_email)):
        # Create a MIME message
    message = MIMEMultipart()
    message["From"] = sender_email
    # message["To"] = receiver_email
    message["To"] = ",".join(receiver_email)
    message["Subject"] = f"Quote for Truck with chassis: {truck_chassis}, Name: {truck_name} and Title: {truck_title}"
    # Create the email body
    body = f"User: {data.name},\nCountry: {data.country}, \nCity: {data.city}, \nPhone: {data.phone}, \nEmail: {data.email}, \nWhatsapp: {data.whatsapp} is asking for a quote for Truck, \nwith remarks: {data.remarks}"
    message.attach(MIMEText(body, "plain"))
    try:
        # Set up the SMTP server and send the email
        with smtplib.SMTP("smtp.zoho.com", 587) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)  # Log in to your email
            # server.sendmail(sender_email, receiver_email, message.as_string())
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Quote email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")


def send_quote_to_email_sparepart(part_name:str, part_make:str, part_model:str, data):

    sender_email = "info@bigstaruae.com"
    sender_password = "j9PYrxJ3eCZt"
    receiver_email = ["info@bigstaruae.com", "moazzamwalikhan@gmail.com", "m.umar@baiggrp.com"]


    # Create a MIME message
    message = MIMEMultipart()
    message["From"] = sender_email
    # message["To"] = receiver_email
    message["To"] = ",".join(receiver_email)
    message["Subject"] = f"Quote for Sparepart with Name: {part_name}, Make: {part_make} and Model: {part_model}"
    # Create the email body
    body = f"User: {data.name},\nCountry: {data.country}, \nCity: {data.city}, \nPhone: {data.phone}, \nEmail: {data.email}, \nWhatsapp: {data.whatsapp} is asking for a quote for Sparepart, \nwith remarks: {data.remarks}"
    message.attach(MIMEText(body, "plain"))
    try:
        # Set up the SMTP server and send the email
        with smtplib.SMTP("smtp.zoho.com", 587) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)  # Log in to your email
            # server.sendmail(sender_email, receiver_email, message.as_string())
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Quote email sent successfully!")
    except Exception as e:
        # import traceback
        # print(f"Error sending email to {receiver_email[i]}: {traceback.format_exc()}")

            print(f"Error sending email: {e}")


"""**********INFORM ADMIN ABOUT NEW USER*************"""
def send_user_details_to_admin(id, fname, lname, email, phone, role):
    try:
        sender_email = "info@bigstaruae.com"
        sender_password = "j9PYrxJ3eCZt"
        receiver_email = ["info@bigstaruae.com ", "moazzamwalikhan@gmail.com", "m.umar@baiggrp.com"]

        # Create a MIME message
        message = MIMEMultipart()
        message["From"] = sender_email
        # message["To"] = receiver_email
        message["To"] = ",".join(receiver_email)
        message["Subject"] = f"Informing about New User registration on Admin waiting for Approval"
        # Create the email body
        body = f"UserID: {id},\nFirst Name: {fname},\nLast Name: {lname},\nEmail: {email},\Phone Number: {phone},\nRole: {role},\nis asking for Approval of Account.\n\n Thank you"
        message.attach(MIMEText(body, "plain"))
        try:
            # Set up the SMTP server and send the email
            with smtplib.SMTP("smtp.zoho.com", 587) as server:
                server.starttls()  # Secure the connection
                server.login(sender_email, sender_password)  # Log in to your email
                # server.sendmail(sender_email, receiver_email, message.as_string())
                server.sendmail(sender_email, receiver_email, message.as_string())
            print("Requesting Approval email sent successfully!")
        except Exception as e:
            print(f"Error sending email: {e}")
            return str(e)
    except Exception as e:
        print(f"Error: {str(e)}")
        return str(e)

"""**********INFORM ADMIN ABOUT Employee Feedback*************"""
def send_user_feedback_to_admin(title, description):
    try:
        sender_email = "info@bigstaruae.com"
        sender_password = "j9PYrxJ3eCZt"
        receiver_email = ["info@bigstaruae.com"]
        # receiver_email = ["m.islamkamran@gmail.com"]

        # Create a MIME message
        message = MIMEMultipart()
        message["From"] = sender_email
        # message["To"] = receiver_email
        message["To"] = ",".join(receiver_email)
        message["Subject"] = f"Employee Feedback"
        # Create the email body
        body = f"Dear Admin,\n\nFeedback from client.\n\nTitle:\n{title}\n\nDescription:\n{description}\n\n Thank you"
        message.attach(MIMEText(body, "plain"))
        try:
            # Set up the SMTP server and send the email
            with smtplib.SMTP("smtp.zoho.com", 587) as server:
                server.starttls()  # Secure the connection
                server.login(sender_email, sender_password)  # Log in to your email
                # server.sendmail(sender_email, receiver_email, message.as_string())
                server.sendmail(sender_email, receiver_email, message.as_string())
            print("Feedback email sent successfully!")
        except Exception as e:
            print(f"Error sending email: {e}")
            return str(e)
    except Exception as e:
        print(f"Error: {str(e)}")
        return str(e)


"""**********INFORM USER FOR WAITING*************"""
def send_user_details_to_user(fname, lname, email):
    try:
        sender_email = "info@bigstaruae.com"
        sender_password = "j9PYrxJ3eCZt"
        receiver_email = [email]

        # Create a MIME message
        message = MIMEMultipart()
        message["From"] = sender_email
        # message["To"] = receiver_email
        message["To"] = ",".join(receiver_email)
        message["Subject"] = f"Informing New User to Wait for Approval"
        # Create the email body
        body = f"Respected {fname} {lname},\nYour account is registered and is waiting for Admin approval you will be inform via email once your registeration is approved.\n\n Best Regards\nBig Star Inc."
        message.attach(MIMEText(body, "plain"))
        try:
            # Set up the SMTP server and send the email
            with smtplib.SMTP("smtp.zoho.com", 587) as server:
                server.starttls()  # Secure the connection
                server.login(sender_email, sender_password)  # Log in to your email
                # server.sendmail(sender_email, receiver_email, message.as_string())
                server.sendmail(sender_email, receiver_email, message.as_string())
            print("Waiting email to user sent successfully!")
        except Exception as e:
            print(f"Error sending email: {e}")
            return str(e)
    except Exception as e:
        print(f"Error: {str(e)}")
        return str(e)


"""**********INFORM USER ABOUT APPROVAL*************"""
def send_user_details_to_client(fname, lname, email,uid,password, role):
    try:

        sender_email = "info@bigstaruae.com"
        sender_password = "j9PYrxJ3eCZt"
        receiver_email = [email]

        # Create a MIME message
        message = MIMEMultipart()
        message["From"] = sender_email
        # message["To"] = receiver_email
        message["To"] = ",".join(receiver_email)
        message["Subject"] = "Account Status Updated"
        # Create the email body
        body = f"Dear User {fname} {lname},\n\nYour account status is updated.\nYou have been assigned the role of: {role}.\nKindly use the Following credentials for logging into your Account.\nUID: {uid}\nPassword: {password}\nWebsite: https://admin.bigstaruae.com/login\n\n Best Regards,\n Big Star Inc."
        message.attach(MIMEText(body, "plain"))
        try:
            # Set up the SMTP server and send the email
            with smtplib.SMTP("smtp.zoho.com", 587) as server:
                server.starttls()  # Secure the connection
                server.login(sender_email, sender_password)  # Log in to your email
                # server.sendmail(sender_email, receiver_email, message.as_string())
                server.sendmail(sender_email, receiver_email, message.as_string())
            print("Requesting Approval email sent successfully!")
        except Exception as e:
            print(f"Error sending email: {e}")
    except Exception as e:
        print(f"Error: {str(e)}")
