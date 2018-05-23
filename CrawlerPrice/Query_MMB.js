// distinct spid
db.getCollection('MMB').aggregate([
    //{$matchurl:{$exists:true}}},
    {$group:{_id:{date:{$dayOfMonth:'$lastcrawl'}, id:'$_id'}}}],
    //{$group:{_id:'_id.date', count:{$sum:1}}}],
    {allowDiskUse:true}
)
    
// distinct bjid
db.getCollection('MMB').aggregate([
    //{$match:{price_multiple:false}},
    {$group:{_id:{date:{$dayOfMonth:'$lastcrawl'}}, count:{$sum:1}}}],
    //{$group:{_id:1, count:{$sum:1}}}
    {allowDiskUse:true}
)

// MMBHist
db.getCollection('MMBHist').find({})
db.getCollection('MMBHist').count({})
db.MMBHist.aggregate([
    {$group:{_id:'$bjid'}},
    {$group:{_id:1, count:{$sum:1}}}
])


// MMB
db.MMB.count()
db.MMB.distinct('spid')
db.MMB_copy.count()

db.MMB.aggregate([
    {$match:{bjid:{$exists:true}, spid:{$exists:true}}},
    {$project:{count:{$sum:1}}}
])



db.MMB.aggregate([
    {$match:{bjid:{$exists:false}}},
    {$group:{_id:{name: '$name', url: '$url', spid: '$spid'}, count:{$sum:1}}},
    {$match:{count:{$gt:1}}},
    //{$count:'count'}
])
    
db.MMB.find().forEach(function(doc){
    var new_url = doc.url.replace('http://www.manmanbuy.com/http://www.manmanbuy.com/', 'http://www.manmanbuy.com/');
    db.MMB.updateOne(
        {'_id':doc._id},
        {'$set':{'url':new_url}}
    );
});
    
db.MMBHist.deleteMany({lastcrawl:{$gt:new Date("2018-04-05")}})

// MMBHist 去重
db.MMBHist.aggregate([
      { $group: { _id: {bjid:'$bjid', spbh:'$spbh', date:'$date', price:'$price'}, dups: { "$addToSet": "$_id" }, count: { "$sum": 1 } }},
      { $match: { count: { "$gt": 1 }}},
      {$out:'MMBHist_dups'}
    ],
    {allowDiskUse: true}
)

db.MMBHist_dups.find().forEach(function(doc) {
    db.MMBHist_copy.deleteMany({_id:{$in:doc.dups}})
})

//MMB去重
db.MMB.aggregate([
      {$match:{bjid:{$exists:true}}},
      {$group: { _id: {bjid:'$bjid', url:'$url', name:'$name', price:'$price', mall:'$mall'}, dups: {"$addToSet": "$_id"}, count: {"$sum": 1}}},
      {$match: { count: { "$gt": 1 }}},
      {$out:'MMB_dups_with_bjid'}
    ],
    {allowDiskUse: true}
)
    
db.MMB.aggregate([
      {$match:{bjid:{$exists:false}}},
      {$group: { _id: {spid:'$spid', url:'$url', name:'$name', price:'$price'}, dups: {"$addToSet": "$_id"}, count: {"$sum": 1}}},
      {$match: { count: { "$gt": 1 }}},
      {$out:'MMB_dups_no_bjid'}
    ],
    {allowDiskUse: true}
)
    
db.MMB_dups_with_bjid.find().forEach(function(doc) {
    db.MMB.deleteMany({_id:{$in:doc.dups}})
})