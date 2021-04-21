from random import randrange


# factory method
def get_templates(driver_name):
    if driver_name== "sqlite":
        return SqliteTemplates()
    else:
        return SqlTemplates()


# parent class for default statements
class SqlTemplates:
    def get_row_count(self, tablename):
        return f"select count(*) as row_count from {tablename};"

    def get_create_table_model(self, table_model, n, d, k, tablename):
        return f"create table {table_model} as select {n} as n, {d} as d, {k} as k, 0 as steps from {tablename} limit 1;"

    def get_add_variance_column(self, table_model):
        return f"alter table {table_model} add variance double;"

    def get_create_table_x(self, normalization, feature_names, d, tablename, table_x):
        if(normalization=="min-max"):
            features_with_alias = ", ".join([f"({feature_names[l]}-min_{l})/(max_{l}-min_{l}) as x_{l}" for l in range(d)])
            min_features = ", ".join([f"min({feature_names[l]}) as min_{l}" for l in range(d)])
            max_features = ", ".join([f"max({feature_names[l]}) as max_{l}" for l in range(d)])
            further_tables = f", (select {min_features}, {max_features} from {tablename}) min_max"
        elif(normalization=="z-score"):
            features_with_alias = ", ".join([f"({feature_names[l]}-avg_{l})/stdev_{l} as x_{l}" for l in range(d)])
            avg_features = ", ".join([f"avg({feature_names[l]}) as avg_{l}" for l in range(d)])
            stdev_features = ", ".join([f"stddev({feature_names[l]}) as stdev_{l}" for l in range(d)]) # TODO: spelling may vary: stdev / stddev
            further_tables = f", (select {avg_features}, {stdev_features} from {tablename}) z_score"
        else:
            features_with_alias = ", ".join([f"{feature_names[l]} as x_{l}" for l in range(d)])
            further_tables = ""
        return f"create table {table_x} as select row_number() over () as i, {features_with_alias} from {tablename}{further_tables};"

    def get_add_cluster_columns(self, table_x):
        return f"alter table {table_x} add min_dist double, add j int;"

    def get_create_table_c(self, d, k, table_c, table_x):
        columns = ", ".join([f"x_{l} as x_{l}_{j}" for j in range(k) for l in range(d)])
        return f"create table {table_c} as select {columns} from {table_x} where i = 1;"

    def get_init_table_c(self, table_c, table_x, n, d, k):
        def get_setters_init(j):
            return ", ".join([f"x_{l}_{j} = x_{l}" for l in range(d)])
        return [f"update {table_c} join {table_x} on i = {randrange(1, n)} set {get_setters_init(j)};" for j in range(k)]
    
    def get_select_models(self):
        return f"select table_name from information_schema.tables where table_name like '%model';"

    def get_select_information(self, table_model):
        return f"select n, d, k, steps, variance from {table_model};"

    def get_set_clusters(self, table_c, table_x, d, k):
        def get_distances(j):
            distance_per_feature = " + ".join([f"power(({table_x}.x_{l} - {table_c}.x_{l}_{j}),2)" for l in range(d)])
            return f"({distance_per_feature}) as dist_{j}"
        distances_to_clusters = ", ".join([get_distances(j) for j in range(k)])
        sub_query_distances = f"select i, {distances_to_clusters} from {table_x}, {table_c} group by i"
        distances_columns = ", ".join([f"dist_{j}" for j in range(k)])
        case_dist_match = " ".join([f"when dist_{j} = sub_table.min_dist then {j}" for j in range(k)])
        return f"update {table_x} join (select *, least({distances_columns}) as min_dist from ({sub_query_distances}) distances) sub_table on sub_table.i = {table_x}.i set {table_x}.min_dist = sub_table.min_dist, j = case {case_dist_match} end;"
            
    def get_update_table_model(self, table_model, n, table_x):
        return f"update {table_model} set steps = steps + 1, variance = (select sum(min_dist)/{n} from {table_x});"

    def get_update_table_c(self, table_c, d, k, table_x):
        def get_sub_selectors(j):
            return ", ".join([f"sum(x_{l})/count(*) as x_{l}_{j}" for l in range(d)])
        def get_setters_move(j):
            return ", ".join([f"{table_c}.x_{l}_{j} = case when sub_table.x_{l}_{j} is null then {table_c}.x_{l}_{j} else sub_table.x_{l}_{j} end" for l in range(d)])
        return [f"update {table_c}, (select {get_sub_selectors(j)} from {table_x} where j={j}) sub_table set {get_setters_move(j)};" for j in range(k)]

    def get_select_visualization(self, table_x, d, k):
        feature_aliases = ", ".join([f"x_{l}" for l in range(d)])
        cluster_examples = " UNION ".join([f"(select {feature_aliases}, j from {table_x} where j = {j} LIMIT 500)" for j in range(k)])
        return f"{cluster_examples};"

 
# class for sqlite specific statements
class SqliteTemplates(SqlTemplates):
    def get_select_models(self):
        return "nothing" # TODO: implement


# class MySqlTemplates(SqlTemplates):
