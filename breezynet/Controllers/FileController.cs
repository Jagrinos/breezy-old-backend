using breezynet.Views;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace breezynet.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class FileController(BreezyContext context) : ControllerBase
    {
        private readonly BreezyContext _context = context;

        [HttpPost]
        public async Task<ActionResult<FileView>> PostFile([FromBody] FileView input, string login)
        {
            try
            {
                var User = await _context.Users.FirstOrDefaultAsync(u => u.Login == login);
                if (User == null) { return BadRequest("user is not found"); }
                Guid guid = Guid.NewGuid(); 
                var newFile = new Models.File() { 
                    Name = guid+input.Name, 
                    Id = guid, 
                    Size = input.Size, 
                    Date = input.Date, 
                    User =  User,
                    UserId = User.Id,
                    };
                User.Files.Add(newFile);
                await _context.SaveChangesAsync();   
                return Ok(
                    new FileView() { 
                        Id = guid.ToString(), 
                        Name = newFile.Name, 
                        Date = newFile.Date, 
                        Size = newFile.Size
                    });
            }
            catch (Exception ex) { 
                return BadRequest(ex.Message);  
            }
        }
    }
}
