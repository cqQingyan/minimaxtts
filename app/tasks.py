from app import create_app, db, socketio, executor
from app.services.minimax import minimax_client
from app.models import History
from datetime import datetime
import time
from flask import current_app

def process_async_task(task_id, user_id, voice_name, text_preview):
    """
    Background task to poll MiniMax API for task status.
    """
    app = create_app()
    with app.app_context():
        try:
            current_app.logger.info(f"Starting poll for task {task_id}")

            # Re-query user/history to ensure we are attached to this session
            history = History.query.filter_by(task_id=str(task_id)).first()
            if not history:
                # This should rarely happen if the main thread committed successfully,
                # but with SQLite WAL or async delays, it's possible.
                # Or if the DB path is different (which we fixed by using abspath in config).
                current_app.logger.warning(f"History not found for task {task_id}, creating new record in background thread.")
                history = History(user_id=user_id, task_id=str(task_id), status='processing',
                                  voice_name=voice_name, text_preview=text_preview)
                db.session.add(history)
                db.session.commit()

            while True:
                resp = minimax_client.query_task(task_id)
                status = resp.get('status')

                current_app.logger.debug(f"Task {task_id} status: {status}")

                if status == 'Success':
                    file_id = resp.get('file_id')
                    file_resp = minimax_client.retrieve_file(file_id)
                    download_url = file_resp.get('file', {}).get('download_url')

                    history.status = 'success'
                    history.file_path = download_url
                    db.session.commit()

                    socketio.emit('task_update', {
                        'task_id': task_id,
                        'status': 'success',
                        'download_url': download_url
                    }, namespace='/')
                    current_app.logger.info(f"Task {task_id} success.")
                    break

                elif status in ['Failed', 'Expired', 'Unknown']:
                    history.status = 'failed'
                    db.session.commit()
                    socketio.emit('task_update', {'task_id': task_id, 'status': 'failed'}, namespace='/')
                    current_app.logger.warning(f"Task {task_id} failed with status {status}")
                    break

                time.sleep(10)

        except Exception as e:
            current_app.logger.error(f"Error in background task {task_id}: {e}", exc_info=True)
            # Try to recover session to log error state if possible
            try:
                if history:
                    history.status = 'error'
                    db.session.commit()
            except:
                pass

def submit_async_generation(text, text_file_id, voice_id, voice_name, user_id, **kwargs):
    """
    Submits the task to MiniMax and starts the polling background task.
    """
    try:
        current_app.logger.info(f"Submitting async task for user {user_id}")
        resp = minimax_client.generate_async(text=text, text_file_id=text_file_id, voice_id=voice_id, **kwargs)
        task_id = resp.get('task_id')

        if not task_id:
            raise ValueError("No task_id returned from API")

        preview = (text[:30] + '...') if text else f"File ID: {text_file_id}"
        history = History(
            user_id=user_id,
            task_id=str(task_id),
            status='processing',
            voice_name=voice_name,
            text_preview=preview
        )
        db.session.add(history)
        db.session.commit()

        # Pass necessary data to background task so it can recreate the record if needed (redundancy)
        executor.submit(process_async_task, task_id, user_id, voice_name, preview)

        return task_id
    except Exception as e:
        current_app.logger.error(f"Failed to submit async task: {e}", exc_info=True)
        raise e
