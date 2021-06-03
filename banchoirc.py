import osu_irc
import asyncio
import os, sys
import json
from tinydb import TinyDB, Query
import time

from auxiliary.constants import *


class MyBot(osu_irc.Client):
  async def onReady(self):
    pass

  async def onMessage(self, message):
    
    osu_user = str(message.Author)
    print(osu_user)
    content = message.content

    if PREFIX in content: # assume its a code
      table = self.db.table('users', cache_size=0) # unlimited cache size may increase speed, but also can be wonky
      Users = Query()
      results = table.search(Users.last_code == content)
      results_by_osu_user = table.search(Users.osu_user == osu_user)

      

      if results == []: # means that user has not used discord bot verification or code is wrong

        await self.sendPM(osu_user, "Invalid code!")

      else:

        user = results[0]
        discord_id = user['discord_user']

        if user['verified'] == False:
            if time.time() - float(user['last_code_time_sent']) <= 60*30: # code was sent within 30 minutes
              if results_by_osu_user == []:# ensure that osu! user is not already linked to an account
              
                # Update verification error (success)

                user['verified'] = True
                user['osu_user'] = osu_user
                user['last_code'] = None
                user['verification_error'] = "success"

                if osu_user not in user['verified_osu_list']:
                  user['verified_osu_list'].append(osu_user)

                table.upsert(user, Users.discord_user == discord_id)

              else:
                # Update verification error (code timeout)
              
                user['verification_error'] = "user_already_linked"

                table.upsert(user, Users.discord_user == discord_id)

            else:

              # Update verification error (code timeout)
              
              user['verification_error'] = "code_timeout"

              table.upsert(user, Users.discord_user == discord_id)
        else:
          # Update verification error (code timeout)
              
              user['verification_error'] = "already_verified"

              table.upsert(user, Users.discord_user == discord_id)





if __name__ == '__main__':

    with open(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'config.json')) as f:
      config_data = json.load(f)

    db = TinyDB(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'database.json'))

    print(config_data['OSU_USER'],config_data['OSU_TOKEN'])
    x = MyBot(token=config_data['OSU_TOKEN'], nickname=config_data['OSU_USER'])
    x.db = db
    x.run()