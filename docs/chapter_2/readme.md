### A Clearer Picture

So things are coming into shape. First version of this thing is going to take a stock symbol (and maybe an exchange)
and return some useful information like:
- Revenue history quarterly / annually
- EPS history q / a
- price history stats


I looked into a few apis and options and it seems that in order to get decent company financials like EPS and revenue,
the most straightforward thing to do is scrape a site like GoogleFinance or Yahoo. For price history data the yahoo-finance
python module looks amazing. It will allow me to get the raw data into a pandas dataframe if I want to -
so there's a good chance a little data-analysis might find it's way in here.


##### Future Considerations

This will lead to all kinds of questions like:

- what happens when Google changes the site layout or functionality?
- how can something like this be FT'd ?
- should i be caching data on the server anywhere along the line ?

But I'll try to tackle these as they come. For now I wanna get started.

***

Given all that data, I think it would be cool to run PASS / FAIL tests on stock's current situation.
There's a kind of geeky inception to using TDD to build an app that itself runs other tests. maybe. whatever.

I'm going to start with a simple test:

**is the stock currently trading within 15% of it's 1yr high?**

that is going to mean using the yahoo-finance library. No web scraping just yet.


I'm all finished with my `poc/yahoo-finance` branch for now, but i'm going to keep it around. As I come back
to master and check out the state of my project, I'm seeing something to improve right away.

It's starting to become a hassle to keep sticking all the tests in a single file. It'll be good to look into a testrunner
like nose or maybe a Flask manage.py approach. This'll also allow me to fix up how those tests are structured a bit.



After that things get a little involved. I'm going to be pulling data from yahoo-finance, and my existing service and FT
code is pretty hardcoded. I need to refactor my code to make requests on the external service. My unit tests


I'm going to have to make a choice here:
- Send actual requets to the external yahoo-service during FTs
- Implement some method of 'faking' the response during FTs

So far I'm seeing pros and cons for each.




Here's my todo list (which will probably evolve along the way):

***
### Agenda:
1. Refactor project to use Flask Manager (`manage.py`)
2. Refactor project to get info from yahoo-finance - Get all tests back to passing
3. Write FT that checks getting 1yr high and current price.
4. Write unit tests for the approach
5. Code till unit tests pass, verifying FT passes at the end
6. Add bootstrap to the app so it looks nicer
***

That's the outer loop (FT), inner-loop (unit test) rythym i'm trying to get down.



Here's the diff that gets the Flask Manager approach (using a `manage.py` file) working:

https://github.com/smrkem/docker-flask-tdd/commit/e78bc2b9743202cfdcea689520d90e1b3d485b53


Now that I have test-discovery, I can split up my tests into folders (that apparently need to be modules with an `__init__.py` file?)
and name them a little better. What I had before was gonna get real messy, real quick.

https://github.com/smrkem/docker-flask-tdd/commit/9b5ec1dae8656e95998efae199dceef8e4f31f06


Things are working pretty good - that `z_acceptance_tests` naming was just cuz I like my FTs to run after all the unit tests.


### 2. Refactor project to get info from yahoo-finance - Get all tests back to passing

I'm going to be adding a YahooFinanceClient as 'source' for the StockData class. I start with a new test file for
services and clients `test_service_clients.py`.  


Ultimately I'm gonna want to be able to get info from a list of sources, maybe depending on what's asked for in the query. For now, the minimal thing is for get_stock_info to call the YahooFinanceClient's get_stock_info.

```

class StockDataTest(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        return app

    @patch('stockdata.services.YahooFinanceClient')
    def test_get_stock_info_calls_source_get_stock_info(self, mock_source):
        mock_source.return_value.get_stock_info.return_value = {"stock":"data"}
        stock = StockData()
        stockdata = stock.get_stock_info("SYMB")
        mock_source.return_value.get_stock_info.assert_called_with("SYMB")
        self.assertEqual(stockdata, {"stock":"data"})

```  

A quick bout of inner TDD and my `services.py` becomes:  
```
from stockdata.sources.YahooFinanceClient import YahooFinanceClient


class StockData:

    def get_stock_info(self, symbol):
        return YahooFinanceClient().get_stock_info(symbol)
```
and I've added a new 'sources' folder (with an __init__.py) for the vary basic `sources/YahooFinanceClient.py`:
```
class YahooFinanceClient:

    def get_stock_info(self, symbol):
        pass
```



[test_messages](../test_messages/message_05.txt)


Notice that now my unit tests are all passing, but the FT broke. That's cool - totally expected and I'll know I've done my job right when the FT passes at the end (though it'll likely need some small modifications)  

Now i add some tests for the YahooFinanceClient - just in the same `test_service_clients.py` file. Along the way I get caught up refactoring my services organization. Looking at the diff:  

https://github.com/smrkem/docker-flask-tdd/commit/4301cb91878abbf1ffca5e10e11624ebb6ffe0f3

I'm not at all sure that was a good idea.

...  

I wasn't even done yet. One more commit before the tests are failing in any way that makes sense.  

https://github.com/smrkem/docker-flask-tdd/commit/2559111e474d614fb2443fdecfdb81ee17218857


And the FT is still failing - expected, but kinda noisy. Next up - another detour to let me use Manager to just run unit_tests.  

https://github.com/smrkem/docker-flask-tdd/commit/0d68e8c480407f9dfc2d71091cfb7fa386393022

That was almost fun. A little hacky and unneccessary - but now I can run just the unit tests with
```
docker-compose run --rm web sh runtests.sh unit
```
(which i've aliased to just `tdddocker-run-tests unit`). And i was also able to get rid of that stupid `z_acceptance_tests` folder name too. Now that I can run just the unit tests, don't care a whole lot if the FTs come first. The majority of my time is spent going back and forth between unit tests and coding - in the inner loop.  




_just had to fix the unit test patching_  
_and also wondering if markdown will respect the 4 blank lines i left above this in atom editor (which keeps getting rid of the 2 blank spaces i'm leaving on each empty line - cuz markdown ... who the fuck knows?)



So the unit tests are failing with:  
- [test_messages](../test_messages/message_06.txt)  

```
AttributeError: <module 'stockdata.services.sources.YahooFinanceClient' from '/usr/src/app/stockdata/services/sources/YahooFinanceClient.py'> does not have the attribute 'Share'
```
_(wow. i'm still learning python's module / package import rules, and those long module name chains *really* feels wrong)_

Stuck a
```
from yahoo_finance import Share
```
in there and also added `yahoo-finance` to my requirements.txt (which means i need to do a `docker-compose buld` again). Had to tidy up the codebase a bit too - embarassing :(  



_speaking of embarassing_, the next failure is:  
```
YahooFinanceClient().get_stock_info()
TypeError: 'module' object is not callable
```

Fixing that, and another round of inner TDD, there's new tests and code:

https://github.com/smrkem/docker-flask-tdd/commit/444508bd5530485bfad999533e7db7ab25952974

and the test failure messages that lead to it:


[test_messages](../test_messages/message_07.txt)

The StockData class is not using a YahooFinanceClient 'source' to query yahoo-finance. I know my code is making the right calls, but no idea if yahoo-finance is returning anything that makes sense with what i'm doing - or anything at all.  

For that I go look at how my FTs are doing - which I can run pretty easily now (using my alias) with:
- `tdddocker-run-tests acceptance`

```

======================================================================
FAIL: test_can_visit_homepage (test_getting_stock_info.NewVisitorTest)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/src/app/tests/acceptance/test_getting_stock_info.py", line 47, in test_can_visit_homepage
    self.check_stock_info_for(("AETI", "American Electric Technologies Inc", "NASDAQ"))
  File "/usr/src/app/tests/acceptance/test_getting_stock_info.py", line 30, in check_stock_info_for
    self.assertIn(value, stockinfo_table.text, "Check {} is in stock info".format(value))
AssertionError: 'American Electric Technologies Inc' not found in 'Symbol AETI\nName American Electric Technologies,\nExchange NCM' : Check American Electric Technologies Inc is in stock info

----------------------------------------------------------------------
Ran 1 test in 6.483s

FAILED (failures=1)
```

That's cool. It's calling yahoo-finance with "AETI" and everythings cool - except yahoo is calling the company something slightly different. I haven't looked at that initial `us_under_4` spreadsheet in forever. don't care about it anymore. Yahoo variation works fine there.

I had been struggling with the choice between leaving my acceptance tests to query the actual external service (which is way easier and less hacky) - or attempting to mock its response.  

Decided for now to keep it making actual requests. I don't plan on running my FTs often and repeatedly, and this way I'm testing the whole system.

On my way to fixing the FTs - i encountered this error:  
```
raise exception_class(message, screen, stacktrace)
selenium.common.exceptions.NoSuchElementException: Message: Unable to locate element: {"method":"id","selector":"errors"}
```

which meant a small refactor to the YahooFinanceClient:
```
def get_stock_info(self, symbol):
    stock = Share(symbol)
    stock_name = stock.get_name()
    if stock_name is None:
        return None

    stock_exchange = stock.get_stock_exchange()
    return {
        "symbol": symbol,
        "name": stock_name,
        "exchange": stock_exchange
    }
```

but other than that, all I needed to do was correct the company names and change the exchange to be whatever those acronyms the yahoo-finance service is returning. Guess I'll get to learn those over time.

All my tests are green:
```
$ tdddocker-run-tests
 * Running on http://127.0.0.1:8943/ (Press CTRL+C to quit)
test_can_visit_homepage (acceptance.test_getting_stock_info.NewVisitorTest) ... ...
ok
test_get_stock_info_calls_source_get_stock_info (unit.test_service_clients.StockDataTest) ... ok
test_get_stock_info_fetches_exchange (unit.test_service_clients.YahooFinanceClientTest) ... ok
test_get_stock_info_fetches_name (unit.test_service_clients.YahooFinanceClientTest) ... ok
test_get_stock_info_gets_share_for_symbol (unit.test_service_clients.YahooFinanceClientTest) ... ok
test_get_stock_info_returns_stock (unit.test_service_clients.YahooFinanceClientTest) ... ok
test_home_view_calls_index_template (unit.test_views.HomeViewTest) ... ok
test_posting_invalid_symbol_returns_error (unit.test_views.HomeViewTest) ... ok
test_posting_symbol_returns_stock_info (unit.test_views.HomeViewTest) ... ok

----------------------------------------------------------------------
Ran 9 tests in 6.482s

OK
```

which feels fantastic. Firing up the server and visiting the app in my browser I have to play around and convince myself it's all good for a while.  
- `docker-compose up -d`


### 3. Write FT that checks getting 1yr high and current price.  
That's all great, but the app still isn't very useful. The whole time i was playing in the browser I was excited thinking about how much more this thing can easily show me.  

Here's the agenda at this point:


***
### Agenda:
1. ~~Refactor project to use Flask Manager (`manage.py`)~~
2. ~~Refactor project to get info from yahoo-finance - Get all tests back to passing~~
3. Write FT that checks getting 1yr high and current price.
4. Write unit tests for the approach
5. Code till unit tests pass, verifying FT passes at the end
6. Add bootstrap to the app so it looks nicer
***

The app can display the stock's current price and 1yr high on the page - seems like a decent idea. But I don't want to test for specific values on those guys. I'm thinking it'll be good to check for numeric values and that's it. I don't even want to check the 1yr high is larger than current price cuz that might not always be true.

My `check_stock_info_for` seems like the best place to do that (and i'll add some structure to my template html to ease the process).
```
def check_stock_info_for(self, stockinfo):
    stockinfo_table = self.browser.find_element_by_id("stock-info")
    for value in stockinfo:
        self.assertIn(value, stockinfo_table.text, "Check {} is in stock info".format(value))
    current_price = stockinfo_table.find_element_by_id("stck-curent-price").text
    year_high = stockinfo_table.find_element_by_id("stck-1yr-high").text
    self.assertTrue(current_price.isdigit())
    self.assertTrue(year_high.isdigit())
```

This may not be the right way to check that - but i guess i'll figure that out when i finish the inner TDD loop. For now the FT fails with
```
Message: Unable to locate element: {"method":"id","selector":"stck-curent-price"}
```
which I can easily remedy with an update to the template, adding :
```
<tr>
  <td>Current Price:</td>
  <td id="stck-curent-price">{{ stock.current_price }}</td>
</tr>
<tr>
  <td>1 Year High:</td>
  <td id="stck-1yr-high">{{ stock.year-high }}</td>
</tr>
```

I leave the outer FT loop, failing with a promising:
```
self.assertTrue(current_price.isdigit())
AssertionError: False is not true
```
and head inwards.

First add some unit tests:
```
@patch('stockdata.services.sources.YahooFinanceClient.Share')
+    def test_get_stock_info_fetches_year_high(self, mock_share):
+        YahooFinanceClient().get_stock_info("SYMB")
+        mock_share.return_value.get_year_high.assert_called_with()
+
+    @patch('stockdata.services.sources.YahooFinanceClient.Share')
+    def test_get_stock_info_fetches_current_price(self, mock_share):
+        YahooFinanceClient().get_stock_info("SYMB")
+        mock_share.return_value.get_price.assert_called_with()
+
+    @patch('stockdata.services.sources.YahooFinanceClient.Share')
def test_get_stock_info_returns_stock(self, mock_share):
    mock_share.return_value.get_stock_exchange.return_value = "TST"
    mock_share.return_value.get_name.return_value = "Test Company Name"
+        mock_share.return_value.get_price.return_value = 2.32
+        mock_share.return_value.get_year_high.return_value = 6.66

    expected_stock = {
        "symbol": "SYMB",
        "name": "Test Company Name",
-            "exchange": "TST"
+            "exchange": "TST",
+            "current_price": 2.32,
+            "year_high": 6.66
    }
    actual_stock = YahooFinanceClient().get_stock_info("SYMB")

```

and then some code to make them pass:
```
class YahooFinanceClient:

    def get_stock_info(self, symbol):
        stock = Share(symbol)
        stock_name = stock.get_name()
        if stock_name is None:
            return None
        stock_exchange = stock.get_stock_exchange()
        current_price = stock.get_price()
        year_high = stock.get_year_high()

        return {
            "symbol": symbol,
            "name": stock_name,
            "exchange": stock_exchange,
            "current_price": current_price,
            "year_high": year_high
        }
```
Perfect. Turns out I need a minor correction to my FTs. Just replacing:
```
self.assertTrue(current_price.isdigit())
self.assertTrue(year_high.isdigit())
```

with
```
self.assertRegexpMatches(current_price, r'^\d+\.\d+$')
self.assertRegexpMatches(year_high, r'^\d+\.\d+$')]
```
and all my tests are passing. Check out the app in the browser and we're starting to get some actual data. It's a bit of a pain having to figure out the right extension for Canadian stocks (OGI.V, BLO.CN) or probably any non-nassaq / nyse traded stock. Maybe i'll add something to make that easier...


***
### Agenda:
1. ~~Refactor project to use Flask Manager (`manage.py`)~~
2. ~~Refactor project to get info from yahoo-finance - Get all tests back to passing~~
3. ~~Write FT that checks getting 1yr high and current price.~~
4. ~~Write unit tests for the approach~~
5. ~~Code till unit tests pass, verifying FT passes at the end~~
6. Add bootstrap to the app so it looks nicer
***

__i have a bad feeling about leaving those wierd module imports too long. need to learn the right approach there.__

-
I'm wondering if a `StockData` class really belongs in services. maybe it's really a controller, but that feels like the view class too. maybe it'll be a model for a stock type object. that feels kinda right but i'm not sure. I'm gonna put it in a 'controllers' folder and also rename the files to not match the class name. I'm finding that's getting in my way.  

at some point i'm just going to have to google "python packages and modules organization" or something like that. and i lost track of the diff for that reorganization. i clearly don't totally get how to use `git rm --cache` properly yet.
-

i've been holding off on the `stock.get_historical(str(last_year), str(today))` stuff but i think i've got a decent approach. I'd want to be able to run different types of queries on the price data - what yahoo-finance returns is a list.

for instance, i think it'd be cool to see a visual representation of the stock's trading volume levels along with the pct change over the past year.

for now, i'll just return a dict keyed by date, with the volume and pct_change. percent change formula is `(new - old) / old`, and i should probably also return the min and max volumes.

-
i start with a new FT, that verifies the price-volume-trend data shows up in the page, outside-in style. For me it's enough to verify the element shows up in the html with the right data squirreled away inside a data attribute.

Finally - some front-end work.

__I might look into using a js framework to test that, given the right data - the visualization will appear correctly. but i'll push that overhead off for now and forego the tdd process for the front-end.__

I took the opportunity to refactor the FTs a bit. I want to be careful now about making tons of expensive calls against the yahoo service.

```
import unittest, json
from selenium import webdriver as wd
from selenium.webdriver.common.keys import Keys
from flask_testing import LiveServerTestCase
from stockdata import app


class NewVisitorTest(LiveServerTestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['LIVESERVER_PORT'] = 8943
        return app

    def setUp(self):
        self.browser = wd.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def submit_stock_symbol(self, symbol):
        inputbox = self.browser.find_element_by_id("in_symbol")
        inputbox.send_keys(symbol)
        inputbox.send_keys(Keys.ENTER)

    def check_stock_info_for(self, stockinfo):
        stockinfo_table = self.browser.find_element_by_id("stock-info")
        for value in stockinfo:
            self.assertIn(value, stockinfo_table.text, "Check {} is in stock info".format(value))
        current_price = stockinfo_table.find_element_by_id("stck-curent-price").text
        year_high = stockinfo_table.find_element_by_id("stck-1yr-high").text
        self.assertRegexpMatches(current_price, r'^\d+\.\d+$')
        self.assertRegexpMatches(year_high, r'^\d+\.\d+$')

    def test_can_visit_homepage(self):
        # Jim needs to get some stock info.
        # He hears about a new app called StockData and goes to the homepage.
        self.browser.get(self.get_server_url())
        self.assertEqual("StockData", self.browser.title)
        self.assertIn("StockData", self.browser.find_element_by_tag_name('h1').text)

        # He sees an input box where he can input a stock symbol
        inputbox = self.browser.find_element_by_id("in_symbol")
        self.assertEqual(inputbox.get_attribute('placeholder'), "Enter a stock symbol")

        # Jim tries to enter some junk to see if the app breaks
        self.submit_stock_symbol("INVALID")
        errors = self.browser.find_element_by_id("errors")
        self.assertIn("Could not find any stock for symbol: 'INVALID'", errors.text)

        # He enters "AETI" and hits Enter.
        self.submit_stock_symbol("AETI")

        # He sees the stock name and stock exchange on the page.
        self.check_stock_info_for(("AETI", "American Electric Technologies", "NCM"))

    def test_can_view_stock_info(self):
        # Jim returns to the app
        self.browser.get(self.get_server_url())

        # He tries a different stock symbol and sees the new name and exchange on the page.
        self.submit_stock_symbol("CRNT")
        self.check_stock_info_for(("CRNT", "Ceragon Networks Ltd", "NMS"))

        # Along with some price-volume trend data
        pv_trend_graph = self.browser.find_element_by_id("price-volume-trend-graph")
        pv_trend_data = json.loads(pv_trend_graph.get_attribute("pv_data"))
        self.assertIsInstance(pv_trend_data, type(list()))
        self.assertGreater(len(pv_trend_data), 2)
```


This fails, with an expected:
```
selenium.common.exceptions.NoSuchElementException: Message: Unable to locate element: {"method":"id","selector":"price-volume-trend-graph"}
```


so, outside-in - about to head to the inner loop.
1. plan the approach
2. write unit tests then code
3. repeat 2 unit FT passes

First i add the necessary to the template - not at all sure about whether or not I should've used quotes around the
`data-pv_data` attribute (name corrected in later commit) - guess I'll find out soon enough. And i'm happy to see I
can move the `test_get_stock_info_returns_stock` function to the StockData tests with basically no effort. Patching
still works unaltered.

https://github.com/smrkem/docker-flask-tdd/commit/8337cd7f409e4b6f119af2af661cecfd2c4738e5

The reason for that change was that I'm going to want the StockData class to be responsible for any data prepping -
it's likely that other sources might return info that needs the same or similar treatment. I don't want to bury that functionaility
inside the source (yahoo finance client) just yet if i can avoid it.

I want percent change for each day, along with some descriptive meta data like the min and max volumes for the entire
period. Something like a pandas DataFrame is gonna be sweet for this. I write some unit tests:

https://github.com/smrkem/docker-flask-tdd/commit/0291c2d256624b9f481957a44cfda221787fcbee

with some encouraging failures.
 ```
 $ tdddocker-run-tests unit
...
======================================================================
FAIL: test_get_stock_info_returns_stock (test_service_clients.StockDataTest)
----------------------------------------------------------------------
...
    self.assertEqual(actual_stock, expected_stock)
AssertionError: {'exchange': 'TST', 'name': 'Test Company N[60 chars]YMB'} != {'name': 'Test Company Name', 'symbol': ...

======================================================================
FAIL: test_get_stock_info_fetches_historical_prices (test_service_clients.YahooFinanceClientTest)
----------------------------------------------------------------------
...
AssertionError: Expected call: get_historical()
Not called

```

I add the new functionality, along with refactoring the stockdata class so it'll be able to do more.   

https://github.com/smrkem/docker-flask-tdd/commit/54b157778b1df4ebe85e8a0fc942070527740cba

including refactoring the tests.

Along the way, my FTs catch a new bug:
```
selenium.common.exceptions.NoSuchElementException: Message: Unable to locate element: {"method":"id","selector":"errors"}
```

i didn't even introduce that intentionally for documentation stuff - cool to see it in action. I'm not handling return values of `None` properly. Earlier in that same message i see:
```
File "/usr/src/app/stockdata/controllers/stockinfo.py", line 10, in get_stock_info
  "name": stockinfo['name'],
TypeError: 'NoneType' object is not subscriptable
```
which is nice and helpful in fixing the bug. I add a new unit test:  


https://github.com/smrkem/docker-flask-tdd/commit/a04ca51801cce2a46db067f73142af212d1395f2

and i'm realizing those unit tests are getting off track and starting to test things they shouldn't. I don't want to get sidetracked, but i'll add
- make service unit tests only test direct class. fix patching up.  
to some kind of a backlog.  

which fails with the same error as above.

An easy fix - but i also need a small correction to the assertion in the unit test.  

- https://github.com/smrkem/docker-flask-tdd/commit/bb9d643e421c5a5b72994b453f903850818c4688

took a little detour to fix a test that was starting to duplicate another:
```
@patch('stockdata.controllers.stockinfo.YahooFinanceClient')
def test_get_stock_info_calls_source_get_stock_info(self, mock_source):
    stock = StockData()
    stockdata = stock.get_stock_info("SYMB")
    mock_source.return_value.get_stock_info.assert_called_with("SYMB")
```
as well as fix another error that had found its way into my unit tests:  
- https://github.com/smrkem/docker-flask-tdd/commit/7f2ce36a93081189191b21c3130505ab30689006  



Now i'm back to the one failing unit test:
```
======================================================================
FAIL: test_get_stock_info_returns_formatted_stock (test_service_clients.StockDataTest)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python3.5/unittest/mock.py", line 1157, in patched
    return func(*args, **keywargs)
  File "/usr/src/app/tests/unit/test_service_clients.py", line 84, in test_get_stock_info_returns_formatted_stock
    self.assertEqual(actual_stock, expected_stock)

```


I started writing new code in the StockData class to get that to pass. The price_history returned by the YahooFinanceClient is a list of dicts. That can easily be used to create a pandas dataframe, which will do all the math for me. It wasn't long before i was getting errors of the nature:
```
File "/usr/src/app/stockdata/controllers/stockinfo.py", line 12, in get_stock_info
  df_historical_data = pd.DataFrame(stockinfo['price_history'])
File "/usr/local/lib/python3.5/site-packages/pandas/core/frame.py", line 325, in __init__
  raise TypeError("data argument can't be an iterator")
TypeError: data argument can't be an iterator
```
which happened when pandas was getting something other than a list - like a mock for example.

I wasn't really following the tdd pattern there. let me just start writing the minimum amount of code to move it a little further.

I get to the point of having another StockData method (`get_pv_trend_data`) with some initial unit tests. What i want to do is verify that given a list, (with keys 'Open', 'Close', and 'Volume'), it'll return the correct, relevant output.

***
I'm kind of refactoring as i go instead of as a regular part of my process - trying to work on that. Here's the commit for the next round:

https://github.com/smrkem/docker-flask-tdd/commit/6aa2d5dfab0daf281ac4096ac9b16fc79ce44575  

and the test messages that got me there:

[test output](../test_messages/10.txt)  

It's becoming more and more difficult to look at the sloppiness in the service unit tests - that part needs some love soon.  

But things are looking pretty good. I flip over to my FTs where i'm getting:
```
$ tdddocker-run-tests acceptance
...
======================================================================
FAIL: test_can_view_stock_info (test_getting_stock_info.NewVisitorTest)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/src/app/tests/acceptance/test_getting_stock_info.py", line 69, in test_can_view_stock_info
    self.assertIsInstance(pv_trend_data, type(list()))
AssertionError: 2.94 is not an instance of <class 'list'>

----------------------------------------------------------------------
Ran 2 tests in 15.307s

```
Ok - cool. I knew i was going to have to take a closer look at how I was passing that price-volume data to the front end.

***
Along the way my view becomes:
```
@app.route('/', methods=['GET', 'POST'])
def index():
    stock = None
    errors = []
    if request.method == 'POST' and request.form['symbol']:
        stock = StockData().get_stock_info(request.form['symbol'])
        if stock is None:
            errors.append("Could not find any stock for symbol: '{}'".format(request.form['symbol']))
        else:
            stock['pv_trend_data'] = json.dumps(stock['pv_trend_data'])
    return render_template('index.html', stock=stock, errors=errors)
```
which breaks my unit tests in a really cryptic and scary way.

```
$ tdddocker-run-tests unit
test_get_pv_trenddata_gets_max_volume (test_service_clients.StockDataTest) ... ok
test_get_pv_trenddata_gets_min_volume (test_service_clients.StockDataTest) ... ok
test_get_pv_trenddata_gets_pv_data (test_service_clients.StockDataTest) ... ok
test_get_pv_trenddata_returns_formatted_data (test_service_clients.StockDataTest) ... ok
test_get_stock_info_calls_source_get_stock_info (test_service_clients.StockDataTest) ... ok
test_get_stock_info_returns_formatted_stock (test_service_clients.StockDataTest) ... ok
test_get_stock_info_returns_none_for_no_results (test_service_clients.StockDataTest) ... ok
test_get_stock_info_fetches_current_price (test_service_clients.YahooFinanceClientTest) ... ok
test_get_stock_info_fetches_exchange (test_service_clients.YahooFinanceClientTest) ... ok
test_get_stock_info_fetches_historical_prices (test_service_clients.YahooFinanceClientTest) ... ok
test_get_stock_info_fetches_name (test_service_clients.YahooFinanceClientTest) ... ok
test_get_stock_info_fetches_year_high (test_service_clients.YahooFinanceClientTest) ... ok
test_get_stock_info_gets_share_for_symbol (test_service_clients.YahooFinanceClientTest) ... ok
test_home_view_calls_index_template (test_views.HomeViewTest) ... ok
test_posting_invalid_symbol_returns_error (test_views.HomeViewTest) ... ok
test_posting_symbol_returns_stock_info (test_views.HomeViewTest) ... ERROR

... ...

AssertionError: Popped wrong request context.  (<RequestContext 'http://localhost/' [POST] of stockdata> instead of <RequestContext 'http://localhost/' [GET] of stockdata>)
```

The traceback isn't very helpful either. Looking in the test code for `test_posting_symbol_returns_stock_info` i see that we're mocking the StockData::get_stock_info return value, and attempting to pass that to `json.dumps` - probably not good. TO test the theory i make a little addition to the test_views.py:
```
@patch('stockdata.views.StockData')
  def test_posting_symbol_returns_stock_info(self, mock_stockdata):
      mock_stockdata.return_value.get_stock_info.return_value = {
          "stock":"data",
          "pv_trend_data": []
      }
```
so that the mock's return value contains the key `json.dumps` is looking for.
```
AssertionError: {'stock': 'data', 'pv_trend_data': '[]'} != {'stock': 'data'}
- {'pv_trend_data': '[]', 'stock': 'data'}
+ {'stock': 'data'}
```
much better failure there, and i could easily get that to passing - but it's worth a look at what i'm doing there. Whose job is it to know that the browser is expecting json back for the pv_trend_data ? Whose job is it to know that the browser is expecting any pv_trend_data at all?


For now, while the app is tiny - every request requires that data. But it'd be nice, and probbly inevitably needed, to be able to toggle off that request. Based on request times it's a fairly expensive query on the api - and it won't be featured in every single view of a stock's info.

I'll leave that decision logic in the view for the time being - but it'll make a separate request to include to pv_trend_data. It'll also dump it to json. This means refactoring - so i actually want to go back to where all my tests were passing, before updating the view to push the FT further. I want all my tests to be passing, so I know when i'm done they should all be passing again along with whatever new tests I add.

***
Now there's going to be multiple calls to the StockData class and it's time to think about DRYing it up a bit. I can imagine keeping `get_stock_info` and having it return, not everything like it currently does, but sort of _'the basics'_ - name, exchange, current_price, etc. For now i think it's ok to leave year_high in there as well.

The view can make a second call (to `get_pv_trend_data`) to populate that part of the stock object it returns. But I don't want to make an additional call to the YahooFinanceClient - that's what I'm trying to minimize here. I suspect ultimately that it's the client which will need the ability to dynamically include that request or not - but for now I think i'll be headed in the right direction to initialize the StockData class with the symbol and a stockinfo property holding what it gets back from the YahooFinanceClient.

Remember - all my tests are passing at this point.  

...  

Frig - i've gotta go back and undo all the `self.stockdata = StockData()` stuff in the tests. I'll need to init the object as part of each test in order to pass the test arguments.

I go and change the test class back, along the way making sure to pass a 'symbol' to the StockData init. Skipping a step in the pure TDD method - but meh.

https://github.com/smrkem/docker-flask-tdd/commit/4014282d19b8ac4b34e89f00c65c0d0787c75a66

Now most of them (7) are failing - all with the same error:
```
stock = StockData("SYMB")
TypeError: object() takes no parameters
```
Here we go!  

A little bit of code and then check the tests:
```
stock = StockData("SYMB")
TypeError: __init__() takes 1 positional argument but 2 were given
```
A minor code addition and:
```
======================================================================
ERROR: test_get_stock_info_returns_formatted_stock (test_service_clients.StockDataTest)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python3.5/unittest/mock.py", line 1157, in patched
    return func(*args, **keywargs)
  File "/usr/src/app/tests/unit/test_service_clients.py", line 74, in test_get_stock_info_returns_formatted_stock
    actual_stock = stock.get_stock_info()
TypeError: get_stock_info() missing 1 required positional argument: 'symbol'

======================================================================
ERROR: test_get_stock_info_returns_none_for_no_results (test_service_clients.StockDataTest)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python3.5/unittest/mock.py", line 1157, in patched
    return func(*args, **keywargs)
  File "/usr/src/app/tests/unit/test_service_clients.py", line 61, in test_get_stock_info_returns_none_for_no_results
    actual_stock = stock.get_stock_info()
TypeError: get_stock_info() missing 1 required positional argument: 'symbol'

======================================================================
FAIL: test_init_calls_source_get_stock_info (test_service_clients.StockDataTest)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python3.5/unittest/mock.py", line 1157, in patched
    return func(*args, **keywargs)
  File "/usr/src/app/tests/unit/test_service_clients.py", line 55, in test_init_calls_source_get_stock_info
    mock_source.return_value.get_stock_info.assert_called_with("SYMB")
  File "/usr/local/lib/python3.5/unittest/mock.py", line 783, in assert_called_with
    raise AssertionError('Expected call: %s\nNot called' % (expected,))
AssertionError: Expected call: get_stock_info('SYMB')
Not called

----------------------------------------------------------------------
Ran 16 tests in 0.077s

FAILED (failures=1, errors=2)

```
the tests are no longer passing the symbol to `get_stock_info` but the class method is expecting it to. Getting that out of the method argument list changes that error to:
```
stockinfo = YahooFinanceClient().get_stock_info(symbol)
NameError: name 'symbol' is not defined
```
Taking the next, crucial step in the StockData refactoring:
```
class StockData:

    def __init__(self, symbol):
        self.stockinfo = YahooFinanceClient().get_stock_info(symbol)
        self.stockinfo['symbol'] = symbol

    def get_stock_info(self):
        if self.stockinfo is None:
            return None

        return {
            "name": self.stockinfo['name'],
            "exchange": self.stockinfo['exchange'],
            "current_price": self.stockinfo['current_price'],
            "year_high": self.stockinfo['year_high'],
            "pv_trend_data": self.get_pv_trend_data(self.stockinfo['price_history'])
        }

     ...
```
I thought that looked really good - but the tests tell me otherwise.   

[test output](../test_messages/10.txt)  

and the tests are taking considerably longer. I'm initing the StockData in those tests without mocking the YahooFinanceClient at all. not good - dammit.  

***

I modify the views test a bit:
```

    @patch('stockdata.views.StockData')
    def test_posting_symbol_returns_stock_info(self, mock_stockdata):
        mock_stockdata.return_value.get_stock_info.return_value = {"stock":"data"}
        mock_stockdata.return_value.get_pv_trend_data.return_value = 'sample pv_trend_data'
        response = self.client.post('/', data={'symbol': 'ANYSYMBOL'})

        self.assertEqual(response.status_code, 200)
        mock_stockdata.return_value.get_stock_info.assert_called_with('ANYSYMBOL')
        self.assertEqual(self.get_context_variable('stock'),
          {"stock":"data", "pv_trend_data": 'sample pv_trend_data'}
        )
```
which fails of course.  

- https://github.com/smrkem/docker-flask-tdd/commit/54a94928722c352c6d23f0cb95d508133b3b5624

- https://github.com/smrkem/docker-flask-tdd/commit/fa4d7913a21582f4e9b9f7951e2561c5007afe91  
-

-  
- found myself in a situation where i want to return None from a StockData("symbol") call.

Here's the final commit, with StockData `__init__` fetching all the data and storing it, with updated, passing tests.  
- https://github.com/smrkem/docker-flask-tdd/commit/a68ea4fabdfd8a1c79c9406b7f3448353b8c49aa  

and the test messages along the way:  
- [test output](../test_messages/11.txt)

The app runs fine locally (`docker-compose up`), and the FTs are failing with a lovely:
```
json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)
```

It'll be the veiws job to know it needs to get the pv_trend_data and also dump that to appropriate json. I'll have to update my veiws tests first.  

Haven't looked at an updated __Agenda__ for a while:

***
### Agenda:
1. ~~Refactor project to use Flask Manager (`manage.py`)~~
2. ~~Refactor project to get info from yahoo-finance - Get all tests back to passing~~
3. ~~Write FT that checks getting 1yr high and current price.~~
4. ~~Write unit tests for the approach~~
5. ~~Code till unit tests pass, verifying FT passes at the end~~
6. ~~Write FT that checks getting price-volume trend data~~
7. Refactor/Write unit tests for the approach
8. Code till unit tests pass, verifying FT passes at the end
9. Write a js front-end for the graph
10. Add bootstrap to the app so it looks nicer  

***

I'm right in the middle of that second outside-inside TDD loop - write FT, refactor till unit tests pass again, write / refactor unit tests, code till unit tests pass again. At the end that FT should pass as well :)  

I update the tests:  
- https://github.com/smrkem/docker-flask-tdd/commit/93157afa46553e00bddc811db69af29c9aafb6ed


and follow the test ouput:
- [test output](../test_messages/12.txt)  

(along the way breaking my unit tests again and fixing them with:  https://github.com/smrkem/docker-flask-tdd/commit/e4df608f29f3a5ba5cc446c8133b07f8b3265037
)

and then some more test refactoring:  
- https://github.com/smrkem/docker-flask-tdd/commit/395df6a03793246d0f8aec2f4c546422f54f75a4

to get everything back to passing! Examining the app in the front end yields the same encouraging result with a real stock symbol. There's a ton of data attached to the `div#price-volume-trend-graph` element which I can see when inspecting the page in chrome browser.


Here's the __Agenda__ current state:

***
### Agenda:
1. ~~Refactor project to use Flask Manager (`manage.py`)~~
2. ~~Refactor project to get info from yahoo-finance - Get all tests back to passing~~
3. ~~Write FT that checks getting 1yr high and current price.~~
4. ~~Write unit tests for the approach~~
5. ~~Code till unit tests pass, verifying FT passes at the end~~
6. ~~Write FT that checks getting price-volume trend data~~
7. ~~Refactor/Write unit tests for the approach~~
8. ~~Code till unit tests pass, verifying FT passes at the end~~
9. Write a js front-end for the graph
10. Add bootstrap to the app so it looks nicer  

***

Like i mentioned - i'm gonna forego looking into different javascript testing frameworks for the front end and just do some straight-up coding.  

I can at least add a view test to ensure the page includes the javascript element with the correct source:  
```

    def test_home_view_loads_javascript(self):
        response = self.client.get('/')
        print(type(response))
        print(dir(response))
        self.assert_template_used('index.html')
```
(i had to resort to introspecting the python object since documentation on flask-testing classes and methods is apparently shit - or at least very, very hard to find. )

### ASIDE: A Rant on my IDE
currently using atom and struggling. haven't spent much time trying to get it set up properly with code indexing and hinting. it'd be nice to be able to jump to file + line in source code and also
see available methods in a dropdown. like pycharm.

i also need to fix my disaster of a shell terminal
***

I end up with:
```

    def test_home_view_loads_javascript(self):
        response = self.client.get('/')
        response = response.data.decode('utf')

        src = url_for('static', filename='stockdata.js')
        expected_tag = "<script src=\"{}\" >".format(src)
        self.assertIn(expected_tag, response)
```
which fails nicely:
```
$ tdddocker-run-tests unit  

...  

======================================================================
FAIL: test_home_view_loads_javascript (test_views.HomeViewTest)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/src/app/tests/unit/test_views.py", line 24, in test_home_view_loads_javascript
    self.assertIn(expected_tag, response)
AssertionError: '<script src="/static/stockdata.js" >' not found in '<html>\n  <head>\n    <title>StockData</title>\n  </head>\n  <body>\n      <h1>StockData</h1>\n      \n      <form method="post">\n        <input type="text" name="symbol" id="in_symbol" placeholder="Enter a stock symbol">\n      </form>\n      \n  </body>\n</html>'

----------------------------------------------------------------------
Ran 18 tests in 0.092s

FAILED (failures=1)
```

And then  
```

    def test_stockdata_javascript_returns_ok(self):
        response = self.client.get(url_for('static', filename='stockdata.js'))
        self.assertEqual(response.status_code, 200)
```
with the failure:
```

======================================================================
FAIL: test_stockdata_javascript_returns_ok (test_views.HomeViewTest)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/src/app/tests/unit/test_views.py", line 29, in test_stockdata_javascript_returns_ok
    self.assertEqual(response.status_code, 200)
AssertionError: 404 != 200

----------------------------------------------------------------------
Ran 19 tests in 0.091s

FAILED (failures=1)
```  

perfect. the tests are telling me what to do next. that's how i want it to be. I add a 'static' folder inside the app along with an empty 'static/stockdata.js' file. Everything passes.

I have a blank stockdata.js file being loaded onto the page. I'm going to be using jQuery to help display the pv-trend-graph. another quick unit test:
```

    def test_home_view_loads_javascript(self):
        response = self.client.get('/')
        response = response.data.decode('utf')

        src = url_for('static', filename='stockdata.js')
        expected_tag = "<script src=\"{}\" >".format(src)
        self.assertIn(expected_tag, response)
```  
And i'm only guessing at this point with the exact regex. Gonna fine tune that as needed. it fails:
```
======================================================================
FAIL: test_home_view_loads_jquery (test_views.HomeViewTest)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/src/app/tests/unit/test_views.py", line 35, in test_home_view_loads_jquery
    self.assertRegex(response, pattern)
AssertionError: Regex didn't match: '<script src=".*code\\.jquery\\.com\\/.*" >' not found in '<html>\n  <head>\n    <title>StockData</title>\n  </head>\n  <body>\n      <h1>StockData</h1>\n      \n      <form method="post">\n        <input type="text" name="symbol" id="in_symbol" placeholder="Enter a stock symbol">\n      </form>\n      \n\n      <script src="/static/stockdata.js" ></script>\n  </body>\n</html>'

----------------------------------------------------------------------
Ran 20 tests in 0.094s

FAILED (failures=1)

```
I add the script tag to my template 'index.js' file - which at the time of writing looks like this:
- `<script src="https://code.jquery.com/jquery-2.2.4.min.js" ></script>`

What that passes I repeat the process for my new `static/style.css` file.
```
$ tdddocker-run-tests unit
...  

======================================================================
FAIL: test_home_view_loads_css (test_views.HomeViewTest)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/src/app/tests/unit/test_views.py", line 47, in test_home_view_loads_css
    self.assertIn(expected_tag, response)
AssertionError: '<link rel="stylesheet" href="/static/style.css" type="text/css">' not found in '<html>\n  <head>\n    <title>StockData</title>\n  </head>\n  <body>\n      <h1>StockData</h1>\n      \n      <form method="post">\n        <input type="text" name="symbol" id="in_symbol" placeholder="Enter a stock symbol">\n      </form>\n      \n\n      <script src="https://code.jquery.com/jquery-2.2.4.min.js" ></script>\n      <script src="/static/stockdata.js" ></script>\n  </body>\n</html>'

======================================================================
FAIL: test_main_css_returns_ok (test_views.HomeViewTest)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/src/app/tests/unit/test_views.py", line 39, in test_main_css_returns_ok
    self.assertEqual(response.status_code, 200)
AssertionError: 404 != 200

----------------------------------------------------------------------
Ran 22 tests in 0.099s

FAILED (failures=2)

```


All tests are passing. Time to get started on that front end.


### LOoking ahead
this thing is gonna incorporate react, and look at testing that with the FT and maybe a javascript testing framework (qunit maybe - but a cli tool would be better)

FTs have a problem with threading? look into the flask-testing LiveServerTestCase and how it handles threading. possibly need to do the  patching in the 'clsSetUp' or whatever function.

***

Going to want to implement some kind of cacheing - enter a db. But initially can begin building the cache system to drive development and testing - ie: save a response to a file and add ability to load that response from 'cache'.
