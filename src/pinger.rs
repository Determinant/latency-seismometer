#[macro_use]
extern crate log;

use clap::{App, Arg};
use fastping_rs::PingResult::{Idle, Receive};
use fastping_rs::Pinger;
use std::fs::File;
use std::io::{self, BufRead, Write};

fn main() {
    env_logger::Builder::new()
        .format(|buf, record| {
            let ts = buf.timestamp();
            writeln!(buf, "{} {} {}", ts, record.level(), record.args())
        })
        .filter(None, log::LevelFilter::Info)
        .init();

    let m = App::new("Latency Seismometer")
        .version("0.1")
        .author("Ted Yin <tederminant@gmail.com>")
        .about("Record ping RTT for hosts")
        .arg(
            Arg::with_name("addr")
                .multiple(true)
                .short("a")
                .long("addr")
                .value_name("HOST")
                .help("add a pinged host")
                .takes_value(true),
        )
        .arg(
            Arg::with_name("list")
                .multiple(true)
                .short("l")
                .long("list")
                .value_name("FILE")
                .help("add hosts from a file")
                .takes_value(true),
        )
        .get_matches();

    let (pinger, results) = match Pinger::new(None, Some(56)) {
        Ok((pinger, results)) => (pinger, results),
        Err(e) => {
            error!("creating pinger: {}", e);
            return
        },
    };

    if let Some(hosts) = m.values_of("addr") {
        for host in hosts {
            pinger.add_ipaddr(host);
        }
    }

    let parse_file = || -> Result<(), String> {
        if let Some(lists) = m.values_of("list") {
            for file in lists {
                let f = File::open(file).map_err(|e| e.to_string())?;
                for host in io::BufReader::new(f).lines() {
                    pinger.add_ipaddr(&host.map_err(|e| e.to_string())?)
                }
            }
        }
        Ok(())
    };

    if let Err(msg) = parse_file() {
        error!("loading file: {}", msg);
        return
    }

    pinger.run_pinger();

    loop {
        match results.recv() {
            Ok(result) => match result {
                Idle { addr } => {
                    error!("Idle Address {}.", addr);
                }
                Receive { addr, rtt } => {
                    info!("{} {:?}.", addr, rtt);
                }
            },
            Err(_) => panic!("Worker threads disconnected before the solution was found!"),
        }
    }
}
