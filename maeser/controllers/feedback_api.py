from flask import request

def controller(session_handler):
    """
    Handle feedback for messages.

    Returns:
        dict: Status of the feedback submission.
    """
    data = request.get_json()
    branch = data.get('branch')
    session_id = data.get('session_id')
    message = data.get('message')
    like = data.get('like')
    index = int(data.get('index'))
    print(f"Received feedback: {'Like' if like else 'Dislike'} for message: {message} at index: {index}")
    # Handle the feedback (e.g., save to a database, log it, etc.)
    session_handler.add_feedback_to_log(branch, session_id, index, like)
    return {"status": "success"}