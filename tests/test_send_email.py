from ccbr_tools.send_email import send_email_msg


def test_send_email():
    assert {
        "Subject": "test email from python",
        "From": "${USER}@hpc.nih.gov",
        "To": "${USER}@hpc.nih.gov",
        "Content-Type": 'text/plain; charset="utf-8"',
        "Content-Transfer-Encoding": "7bit",
        "MIME-Version": "1.0",
    } == dict(send_email_msg(text="hello world", debug=True))
