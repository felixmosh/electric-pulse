import uasyncio
import webapp


loop = uasyncio.get_event_loop()
loop.create_task(webapp.start())
loop.run_forever()
