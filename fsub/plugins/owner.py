from fsub import *
import os
import re
import subprocess
import sys
import traceback
from io import StringIO
from time import time
from pyrogram import filters


async def aexec(code, client, message):
    exec(
        "async def __aexec(c, m): "
            + "\n p = print"
            + "\n r = m.reply_to_message"
            + "\n chat = m.chat.id"
        + "".join(f"\n {a}" for a in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)


@Bot.on_message(filters.command("eval") & filters.user(ADMINS))
async def executor(client, message):
    if len(message.command) < 2:
        return await message.reply("<b>berikan saya perintah ?</b>")
    try:
        cmd = message.text.split(" ", maxsplit=1)[1]
    except IndexError:
        return await message.delete()
    t1 = time()
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    redirected_error = sys.stderr = StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexec(cmd, client, message)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = "\n"
    if exc:
        evaluation += exc
    elif stderr:
        evaluation += stderr
    elif stdout:
        evaluation += stdout
    else:
        evaluation += "Success"
    final_output = f"<b>⥤ ʀᴇsᴜʟᴛ :</b>\n<pre language='python'>{evaluation}</pre>"
    if len(final_output) > 4096:
        filename = "output.txt"
        with open(filename, "w+", encoding="utf8") as out_file:
            out_file.write(str(evaluation))
        t2 = time()
        
        await message.reply_document(
            document=filename,
            caption=f"<b>⥤ ᴇᴠᴀʟ :</b>\n<code>{cmd[0:980]}</code>\n\n<b>⥤ ʀᴇsᴜʟᴛ :</b>\nAttached Document",
            quote=False,
        )
        await message.delete()
        os.remove(filename)
    else:
        t2 = time()
        
        await message.reply(final_output)


@Bot.on_message(filters.command("sh") & filters.user(ADMINS))
async def shellrunner(client, message):
    if len(message.command) < 2:
        return await message.reply("<b>ᴇxᴀᴍᴩʟᴇ :</b>\n/sh git pull")
    text = message.text.split(None, 1)[1]
    if "\n" in text:
        code = text.split("\n")
        output = ""
        for x in code:
            shell = re.split(""" (?=(?:[^'"]|'[^']*'|"[^"]*")*$)""", x)
            try:
                process = subprocess.Popen(
                    shell,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                stdout, stderr = process.communicate()
                output += f"<b>{x}</b>\n"
                output += stdout.decode("utf-8") if stdout else ""
                output += stderr.decode("utf-8") if stderr else ""
                output += "\n"
            except Exception as err:
                await message.reply(f"<b>ERROR :</b>\n<pre>{err}</pre>")
    else:
        shell = re.split(""" (?=(?:[^'"]|'[^']*'|"[^"]*")*$)""", text)
        for a in range(len(shell)):
            shell[a] = shell[a].replace('"', "")
        try:
            process = subprocess.Popen(
                shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = process.communicate()
            output = stdout.decode("utf-8") if stdout else ""
            output += stderr.decode("utf-8") if stderr else ""
        except Exception as err:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            errors = traceback.format_exception(
                etype=exc_type,
                value=exc_obj,
                tb=exc_tb,
            )
            return await message.reply(f"<b>ERROR :</b>\n<pre>{''.join(errors)}</pre>")
    if str(output) == "\n":
        output = None
    if output:
        if len(output) > 4096:
            with open("output.txt", "w+") as file:
                file.write(output)
            await client.send_document(
                message.chat.id,
                "output.txt",
                reply_to_message_id=message.id,
                caption="<code>Output</code>",
            )
            return os.remove("output.txt")
        await message.reply(f"<b>OUTPUT :</b>\n<pre>{output}</pre>")
    else:
        await message.reply("<b>OUTPUT :</b>\n<code>None</code>")
