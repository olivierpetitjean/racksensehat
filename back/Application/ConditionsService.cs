using NetApi.Domain;
using NetApi.Infrastructure.Persistence;

namespace NetApi.Application;

public class ConditionsService(AppDbContext db)
{
    private readonly AppDbContext db = db;

    public List<Condition> GetAll()
    {
        return db.Conditions.ToList();
    }

    public void ReplaceAll(List<Condition> conditions)
    {
        db.Conditions.RemoveRange(db.Conditions);
        db.Conditions.AddRange(conditions);
        db.SaveChanges();
    }
}
