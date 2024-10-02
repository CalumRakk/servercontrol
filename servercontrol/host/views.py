from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from host.task import go_to_url, start_browser, stop_browser, get_status
from celery.result import AsyncResult
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from labcontrol.constants import Action


class BrowserControlView(APIView):
    def post(self, request):
        # {"action": "startBrowser"}
        # {"action": "go_to_url","url": "https://www.google.com"}
        # {"action": "checkTask","task_id": "d9e268c1-65bb-47d8-8326-2395c33541d9"}
        # {"action": "getStatus"}
        action_data = request.data.get("action", "")

        if not hasattr(Action, action_data):
            return Response({"message": "error"}, status=400)

        action = getattr(Action, action_data)
        if action == Action.startBrowser:
            task = start_browser.delay()
            return Response(
                {"action": action.value, "status": task.status, "task_id": task.id}
            )
        elif action == Action.go_to_url:
            url = request.data.get("url", "")
            if not (isinstance(url, str) and url.startswith("http")):
                return Response({"message": "error"}, status=400)

            task = go_to_url.delay(url)
            return Response(
                {"action": action.value, "status": task.status, "task_id": task.id}
            )
        elif action == Action.checkTask:
            task_id = request.data.get("task_id", "asdsa")
            result = None
            task = AsyncResult(task_id)
            if task.ready():
                result = task.get()

            return Response(
                {
                    "action": action.value,
                    "status": task.status,
                    "result": result,
                    "info": task.info,
                }
            )
        elif action == Action.getStatus:
            task = get_status.delay()
            return Response(
                {"action": action.value, "status": task.status, "task_id": task.id}
            )
        return Response({"message": "error"}, status=400)

        # elif action == "go_to_url":
        #     url = data.get("url")
        #     browser_go_to_url.delay(url)

        # conn.set("status", json.dumps(status))
        # return JsonResponse(status, status=200)


# def get_browser_status(request) -> HttpResponse:
#     logger.info("solicitud http get_browser_status")
#     browser_status = utils.get_browser_status()
#     data = {"browser_status": browser_status.translate}
#     json_data = json.dumps(data)
#     response = HttpResponse(json_data, content_type="application/json")
#     response["Access-Control-Allow-Origin"] = "*"
#     logger.info(f"respuesta http get_browser_status {json_data}")
#     return response

# def get_status(request) -> HttpResponse:
#     logger.info("solicitud http get_status")
#     browser_status = utils.get_browser_status()
#     pc_status = utils.get_pc_status()
#     data = {
#         "browser_status": browser_status.translate,
#         "pc_status": pc_status.translate,
#     }
#     # json_data = json.dumps(data)
#     # response = HttpResponse(json_data, content_type="application/json")
#     # response["Access-Control-Allow-Origin"] = "*"
#     return JsonResponse(data)


def aws(request):
    # try:
    #     if request.method == "POST":
    #         try:
    #             body = json.loads(request.body)
    #         except json.JSONDecodeError:
    #             pass

    #         if body["a"] == "turnOnBrowser":
    #             logger.info("action turnOnBrowser")
    #             load_browser.delay()
    #             return "loading browser"
    # except:
    #     pass

    return render(
        request,
        "host/index.html",
        {},
    )
