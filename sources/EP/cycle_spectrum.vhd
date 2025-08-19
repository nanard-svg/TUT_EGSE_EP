library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity cycle_spectrum is
    port(
        sys_clk                : in  std_logic;
        reset                  : in  std_logic;
        i_detector_number      : in  unsigned;
        o_clk_synchro_spectrum : out std_logic;
        o_enable_cycle_spectrum: out std_logic
    );
end entity cycle_spectrum;

architecture RTL of cycle_spectrum is

    type state_type is (init, run);
    signal state : state_type := init;

    signal init_count_synchro_spectrum : unsigned(26 downto 0);
    signal count_synchro_spectrum      : unsigned(26 downto 0);
    signal clk_synchro_spectrum        : std_logic;

begin

    process(sys_clk, reset) is
    begin
        if reset = '1' then
            state                       <= init;
            count_synchro_spectrum      <= (others => '0');
            init_count_synchro_spectrum <= (others => '0');
            clk_synchro_spectrum        <= '0';
            o_enable_cycle_spectrum     <= '0';

        elsif rising_edge(sys_clk) then

            case state is
                when init =>

                    init_count_synchro_spectrum <= init_count_synchro_spectrum + 1;
                    if To_integer(init_count_synchro_spectrum) >= (2056 * To_integer(i_detector_number)) then
                        state <= run;
                    end if;

                when run =>
                    
                    o_enable_cycle_spectrum <= '1';
                    count_synchro_spectrum <= count_synchro_spectrum + 1;
                    if To_integer(count_synchro_spectrum) >= 20000000 then
                        clk_synchro_spectrum   <= not clk_synchro_spectrum;
                        count_synchro_spectrum <= (others => '0');
                    end if;

            end case;
        end if;
    end process;

    o_clk_synchro_spectrum <= clk_synchro_spectrum;

end architecture RTL;
