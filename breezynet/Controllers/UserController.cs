using breezynet.Models;
using breezynet.Views;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace breezynet.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class UserController(BreezyContext context) : ControllerBase
    {
        private readonly BreezyContext _context = context;

        [HttpGet("allusers")]
        public async Task<ActionResult<List<UserView>>> GetUsers()
        {
            return Ok(await _context.Users.ToListAsync());
        }
        [HttpPost("authorization")]
        public async Task<ActionResult> Authorization([FromBody] UserView user)
        {
            var foundUser = await _context.Users.FirstOrDefaultAsync(u => u.Login ==  user.Login);
            if (foundUser is null || !BCrypt.Net.BCrypt.Verify(user.Password,foundUser.Password)) {
                return BadRequest("Login or password error");         
            }
            return Ok("User is found");
        }
        [HttpPost("register")]
        public async Task<ActionResult> Register([FromBody] UserView user)
        {
            try
            {
                if (await _context.Users.FirstOrDefaultAsync(u => u.Login == user.Login) != null)
                    throw new Exception("Login is already in use");

                string hashedPassword = BCrypt.Net.BCrypt.HashPassword(
                        inputKey: user.Password, 
                        salt: BCrypt.Net.BCrypt.GenerateSalt()
                    );
                await _context.Users.AddAsync(
                    new User() {
                        Id = Guid.NewGuid(), 
                        Login = user.Login!, 
                        Password = hashedPassword
                    }
                    );
                await _context.SaveChangesAsync();
                
                return Created();
            }
            catch (Exception ex)
            {
                return BadRequest(ex.Message);
            }
        }

        [HttpDelete("delall")]
        public async Task<ActionResult> DeleteAll()
        {
            try
            {
                await _context.Users.Where(u => true).ExecuteDeleteAsync();
                await _context.SaveChangesAsync();
                return Ok("Delete success");
            }
            catch (Exception ex)
            {
                return BadRequest(ex.Message);
            }
        }
    }
}
