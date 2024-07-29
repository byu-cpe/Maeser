from flask import render_template

from maeser.user_manager import UserManager


def controller(
    user_manager: UserManager,
    app_name: str | None = None,
    main_logo_light: str | None = None,
    main_logo_dark: str | None = None,
    chat_head: str | None = None,
    favicon: str | None = None,
):
    print(len(user_manager.authenticators))
    return render_template(
        template_name_or_list="user_management.html",
        user_manager=user_manager,
        users=user_manager.list_users(),
        main_logo_light=main_logo_light,
        main_logo_dark=main_logo_dark,
        chat_head=chat_head,
        favicon=favicon,
        app_name=app_name if app_name else "Maeser",
        # Builtin functions not normally in Jinja templates
        len=len,
    )
