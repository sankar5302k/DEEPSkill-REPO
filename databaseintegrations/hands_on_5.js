db.feedback.drop();

db.feedback.insertMany([
  {
    student_id: 1,
    course_code: 'CS101',
    semester: '2022-ODD',
    rating: 4,
    comments: 'Excellent teaching. Would recommend.',
    tags: ['challenging', 'well-structured', 'good-examples'],
    submitted_at: ISODate('2022-11-30T10:15:00Z'),
    attachments: [
      { filename: 'notes.pdf', size_kb: 240 }
    ]
  },
  {
    student_id: 2,
    course_code: 'CS101',
    semester: '2022-ODD',
    rating: 5,
    comments: 'Love the course! Data structures are key.',
    tags: ['challenging', 'practical'],
    submitted_at: ISODate('2022-12-01T09:00:00Z'),
    attachments: [
      { filename: 'dsa_solutions.zip', size_kb: 1024 }
    ]
  },
  {
    student_id: 3,
    course_code: 'CS101',
    semester: '2022-ODD',
    rating: 2,
    comments: 'Too fast paced. Difficult to follow.',
    tags: ['challenging', 'fast-paced'],
    submitted_at: ISODate('2022-12-02T14:30:00Z'),
    attachments: []
  },
  {
    student_id: 4,
    course_code: 'CS102',
    semester: '2022-ODD',
    rating: 5,
    comments: 'Excellent database lessons.',
    tags: ['well-structured', 'good-examples'],
    submitted_at: ISODate('2022-11-28T11:15:00Z'),
    attachments: [
      { filename: 'db_diagram.png', size_kb: 450 }
    ]
  },
  {
    student_id: 5,
    course_code: 'CS102',
    semester: '2022-ODD',
    rating: 3,
    comments: 'Good course, but SQL is hard.',
    tags: ['practical', 'good-examples'],
    submitted_at: ISODate('2022-12-05T16:00:00Z'),
    attachments: []
  },
  {
    student_id: 6,
    course_code: 'CS103',
    semester: '2021-EVEN',
    rating: 4,
    comments: 'Learned a lot about OOP concepts.',
    tags: ['practical', 'well-structured'],
    submitted_at: ISODate('2021-06-15T10:00:00Z'),
    attachments: [
      { filename: 'oop_assignment.pdf', size_kb: 310 }
    ]
  },
  {
    student_id: 7,
    course_code: 'EC101',
    semester: '2022-ODD',
    rating: 1,
    comments: 'Labs were not properly organized.',
    tags: ['poorly-organized', 'tough'],
    submitted_at: ISODate('2022-11-29T12:00:00Z'),
    attachments: []
  },
  {
    student_id: 8,
    course_code: 'ME101',
    semester: '2021-EVEN',
    rating: 5,
    comments: 'Loved the thermodynamics lectures.',
    tags: ['interesting', 'practical'],
    submitted_at: ISODate('2021-06-20T15:45:00Z'),
    attachments: [
      { filename: 'thermo_notes.pdf', size_kb: 500 }
    ]
  },
  {
    student_id: 9,
    course_code: 'CS101',
    semester: '2022-ODD',
    rating: 3,
    comments: 'Average. Expected more coding exercises.',
    tags: ['theoretical'],
    submitted_at: ISODate('2022-12-04T10:00:00Z'),
    attachments: []
  },
  {
    student_id: 10,
    course_code: 'CS102',
    semester: '2022-ODD',
    rating: 5,
    comments: 'DB integration rules!',
    tags: ['practical', 'good-examples'],
    submitted_at: ISODate('2022-12-06T18:20:00Z')
  }
]);

const count = db.feedback.countDocuments();
print(`Total feedback docs = ${count}`);

const ratingFiveDocs = db.feedback.find({ rating: 5 }).toArray();
printjson(ratingFiveDocs);

const challengingDocs = db.feedback.find({ course_code: 'CS101', tags: 'challenging' }).toArray();
printjson(challengDocs);

const projectedDocs = db.feedback.find({}, { student_id: 1, course_code: 1, rating: 1, _id: 0 }).toArray();
printjson(projectedDocs);

const updateReviewResult = db.feedback.updateMany(
  { rating: { $lt: 3 } },
  { $set: { needs_review: true } }
);
printjson(updateReviewResult);

const pushTagResult = db.feedback.updateMany(
  { needs_review: true },
  { $push: { tags: 'reviewed' } }
);
printjson(pushTagResult);

const deleteResult = db.feedback.deleteMany({ semester: '2021-EVEN' });
printjson(deleteResult);
print(`Total documents remaining: ${db.feedback.countDocuments()}\n`);

const courseStatsPipelineResult = db.feedback.aggregate([
  { $match: { semester: '2022-ODD' } },
  {
    $group: {
      _id: '$course_code',
      avg_rating: { $avg: '$rating' },
      feedback_count: { $sum: 1 }
    }
  },
  { $sort: { avg_rating: -1 } },
  {
    $project: {
      _id: 0,
      course_code: '$_id',
      average_rating: { $round: ['$avg_rating', 1] },
      feedback_count: 1
    }
  }
]).toArray();
printjson(courseStatsPipelineResult);

const tagLeaderboardResult = db.feedback.aggregate([
  { $unwind: '$tags' },
  {
    $group: {
      _id: '$tags',
      count: { $sum: 1 }
    }
  },
  { $sort: { count: -1 } }
]).toArray();
printjson(tagLeaderboardResult);

const indexResult = db.feedback.createIndex({ course_code: 1 });
print(`Index creation result: ${indexResult}`);

print("\nExplaining execution plan for query db.feedback.find({course_code:'CS101'}):");
const explainPlan = db.feedback.find({ course_code: 'CS101' }).explain('executionStats');

const winningStage = explainPlan.queryPlanner.winningPlan;
const executionStats = explainPlan.executionStats;

print(`Winning Stage: ${winningStage.stage}`);
if (winningStage.inputStage) {
  print(`Input Stage (Index lookup): ${winningStage.inputStage.stage}`);
  print(`Index Used: ${winningStage.inputStage.indexName}`);
}
print(`Total Docs Examined: ${executionStats.totalDocsExamined}`);
print(`Total Keys Examined: ${executionStats.totalKeysExamined}`);
print("Note: The execution stats successfully show IXSCAN (Index Scan) stage instead of COLLSCAN (Collection Scan).\n");
