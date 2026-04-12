using NetApi.Domain;
using NetApi.Infrastructure.Persistence;

namespace NetApi.Application;

public class ConditionsService(AppDbContext db)
{
    private readonly AppDbContext db = db;

    public List<Condition> GetAll()
    {
        return db.Conditions
            .OrderBy(condition => condition.MinTemp1)
            .ThenBy(condition => condition.MinTemp2)
            .ToList();
    }

    public void ReplaceAll(List<Condition> conditions)
    {
        db.Conditions.RemoveRange(db.Conditions);
        db.Conditions.AddRange(conditions);
        db.SaveChanges();
    }
}
