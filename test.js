
                function run(x){
                    var date = new Date(x);
                    console.log(date.getFullYear());
                    console.log(date.getMonth());
                    console.log(date.getDate());
                    console.log(date.getHours());
                    console.log(date.getMinutes());
                    console.log(date.getSeconds());
                    console.log(date.getMilliseconds());
                    console.log(date.getTimezoneOffset());
                }
            run('Thu Oct 19 2017 21:50:06 GMT-0400 (Eastern Daylight Time)');