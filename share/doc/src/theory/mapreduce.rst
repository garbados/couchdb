MapReduce
=========

MapReduce is an algorithm for slicing and dicing large datasets across
distributed computing systems, such as Cloudant clusters.

A MapReduce program has two parts:

-  a ``map`` function, which processes documents from your dataset into
   key-value pairs.

-  a ``reduce`` function, which combines the set returned by map -- or
   the results of previous ``reduce`` functions -- into a single value
   per key.

Keep reading to see how it works at Cloudant, or head to our blog to
read about the math and science behind MapReduce with some `foundational
MapReduce
literature <https://cloudant.com/blog/cloudant-labs-on-foundational-mapreduce-literature/>`__.

Batch vs Incremental
--------------------

There are numerous implementations of MapReduce, each with their own
strengths and weaknesses. Systems like Hadoop, unless augmented,
optimize to perform MapReduce in batches, where a MapReduce program is
executed on the dataset as it stood at the time. If the dataset changes,
then to get an updated value for the MapReduce program, you'll have to
run it all over again. This is a showstopper for queries you want
realtime updates for, or for datasets that change frequently.

For secondary indexes, Cloudant uses an implementation of MapReduce
which works incrementally. When you insert or update a document, rather
than rerun the program on the entire dataset, we compute only for the
documents that changed, and the ``reduce`` results those documents
impact, so you can access MapReduce results in only the time it takes to
read them from disk, rather than the time it takes to compute them anew.

Secondary Indexes
-----------------

In Cloudant, secondary indexes -- sometimes called "views" -- are
MapReduce programs written in JavaScript. Below, we'll discuss their
component parts: map and reduce functions. For information on writing
the design documents that hold secondary indexes, see `Creating or
updating a design
document <http://docs.cloudant.com/api/design-documents-get-put-delete-copy.html#creating-or-updating-a-design-document>`__.

Map
~~~

``map`` functions emit a key and value. The key is used for sorting and
grouping, while the value is consumed by the reduce function to reduce
the dataset to a single value. Let's take a look at a map function:

::

    function(doc){
      // if the doc is an event
      if(doc.type === "event"){
        // emit the event's location as a key
        // and emit its number of attendees as the value
        emit(doc.location, doc.attendees);
      }
    }

This will let us sort and group events by location, and use a reduce
value to, for example, sum the number of attendees. The result of this
map over a dataset might look something like this:

::

    {
      "total_rows": 3,
      "offset": 0,
      "rows": [
        {
          // the document's ID
          "id": "eac6f1faf2cc8dd6fbbbb5205c001763",
          // the key we emitted
          "key": ["France", "Paris"],
          // the value we emitted
          "value": 67
        },
        {
          "id": "eac6f1faf2cc8dd6fbbbb5205c0021ce",
          "key": ["UK", "Bristol"],
          "value": 32
        },
        {
          "id": "986d02a1d491fe906856609e9935fa47",
          "key": ["USA", "Boston"]
          "value": 194
        },
        {
          "id": "ecfaf6648cec1f8f1f7c6b365c1115f4",
          "key": ["UK", "Bristol"],
          "value": 45
        }
      ]
    }

Both keys and values can be any valid JSON data structure: strings,
numbers, arrays, or objects.

Check out `query
options <http://docs.cloudant.com/api/design-documents-querying-views.html#query-arguments>`__
for all the options you can use to modify ``map`` results.

Reduce
~~~~~~

*If at all possible, don't use custom reduce functions! Use this section
to learn about how reduces work, but prefer the built-in functions
outlined in the next section. They are simpler, faster, and will save
you time.*

Let's say we wanted to sum up all the values a map function emitted.
That operation would be done in the reduce function.

Reduces are called with three parameters: key, values and rereduce.

-  keys will be a list of keys as emitted by the map or, if rereduce is
   true, null.

-  values will be a list of values for each element in keys, or if
   rereduce is true, a list of results from previous reduce functions.

-  rereduce will be true or false.

Here's an example that finds the largest value within the dataset:

::

    function (key, values, rereduce) {
      // Return the maximum numeric value.
      var max = -Infinity
      for(var i = 0; i < values.length; i++)
        if(typeof values[i] == 'number')
          max = Math.max(values[i], max)
      return max
    }

**ReReduce**
^^^^^^^^^^^^

Reduce functions can be given either the results of map functions, or
the results of reduce functions that already ran. In that latter case,
rereduce is true, because the reduce function is re-reducing the data.
(Get it?)

This way, nodes reduce datasets more quickly by handling both map
results and, once that's all been processed, newly computed reduce
values.

Here's a simple reduce function that counts values, and handles for
rereduce:

::

    function(keys, values, rereduce){
      if(rereduce){
        // values = [4, 5, 6], indicating previous jobs that counted 4, 5, and 6 documents respectively.
        return sum(values);
      }else{
        // values = [{...}, {...}], indicating processed `map` results.
        return values.length;
      }
    }

For the mathematically inclined: operations which are both
`commutative <http://en.wikipedia.org/wiki/Commutative_property>`__ and
`associative <http://en.wikipedia.org/wiki/Associative_property>`__ need
not worry about rereduce.

**Built-in Reduces**
~~~~~~~~~~~~~~~~~~~~

Cloudant exposes several built-in reduce functions which, because
they're written in Cloudant's native Erlang rather than JavaScript, run
much faster than custom functions.

**\_sum**
^^^^^^^^^

Given an array of numeric values, ``_sum`` just, well, sums them up. Our
`Chained MapReduce
example <http://examples.cloudant.com/sales/_design/sales/index.html>`__
uses ``_sum`` to report the best sales months and top sales reps. Here's
an example view:

::

    "map": "function(doc){
      if (doc.rep){ 
        emit({"rep": doc.rep}, doc.amount); 
      }
    }",
    "reduce": "_sum"

This yields sales by rep. Queried without options, the view will report
the total sales for all reps. But, if you group the results using
group=true, you'll get sales by rep.

``_sum`` works for documents containing objects and arrays with numeric
values inside of them, as long as the structure of those documents is
consistent. So, two documents like...

::

    [
      {
        "x": 1,
        "y": 2,
        "z": 3
      },
      {
        "x": 4,
        "y": 5,
        "z": 6
      }
    ]

... sum to {"x":5, "y":7, "z":9}.

**\_count**
^^^^^^^^^^^

``_count`` reports the number of docs emitted by the map function,
regardless of the emitted values' types. Consider this example:

"map": "function(doc){ if(doc.type === "event"){ emit(doc.location,
null); } }", "reduce": "\_count"

If we grouped by key, this would tell us how many events happened at
each location.

**\_stats**
^^^^^^^^^^^

Like ``_sum`` on steroids, ``_stats`` produces a JSON structure
containing the sum, count, min, max and sum squared. Also like ``_sum``,
``_stats`` only deals with numeric values and arrays of numbers; it'll
get mighty angry if you start passing it strings or objects. Consider
how you might use ``_stats`` to get statistics about shopping cart
interactions:

::

    "map": "function(doc){
      if(doc.type === "stock"){
        emit([doc.stock_symbol, doc.created_at.hour], doc.value); 
      }
    }",
    "reduce": "_stats"

With ``group=true&group_level=1``, which groups results on the first
key, you'll get stats per symbol across all time. With
``group=true&group_level=2``, you'll get stats for trades by stock
symbol by hour. Nifty, eh?

Chained Indexes
---------------

For particularly complex queries, you may need to run a dataset through
multiple transformations to get the information you need. For that,
Cloudant allows you to chain secondary indexes together, by inserting
the results of a map function into another database as documents. Let's
see how we do that:

::

    {
      "map": "function(doc){
        if(doc.type === 'event'){
          emit(doc.location, doc.attendees);
        }
      }",
      "dbcopy": "other_database"
    }

This will populate other\_database (or whatever database you indicate)
with the results of that map function, like this:

::

    {
      "id": "eac6f1faf2cc8dd6fbbbb5205c0021ce",
      "key": ["UK", "Bristol"],
      "value": 32
    }

You can then write secondary indexes for ``other_database`` that
manipulate the results accordingly, potentially including secondary
indexes that use ``dbcopy`` again to emit another transformation to
another database.
